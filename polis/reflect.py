"""Layer 3 — evidence-mined self-amendments.

`polis reflect` reads settled-contract history and proposes amendments to the
protocol itself when it detects a recurring *process* pathology (not a one-off
task lesson — those already auto-inject as guardrails). It only ever *proposes*:
files land in `amendments/proposed/` with `status: proposed`, authored by the
system citizen `polis-reflector`. Ratification stays with the citizens via the
normal amendment vote/quorum flow — nothing here changes the constitution itself.

This is the second-order loop: the team's settled history feeds back into the
team's *rules*, with every proposal citing the contracts that motivated it.

Detectors (all derived from settled contracts; no chronicle parsing required):
  - chronic-misroute       : the router's favoured citizen for a tag is consistently
                             out-performed by a peer with enough of a track record.
  - recurring-low-quality  : a tag whose settled work chronically averages low quality.
  - stakes-miscalibration  : low-quality settlements on a tag that were never flagged
                             high-stakes / sent to chavruta review.
"""
import datetime
from pathlib import Path

import yaml

from . import report as _report
from ._io import atomic_write_text
from .routing import parse_frontmatter

REFLECTOR = "polis-reflector"
LOW_QUALITY = 2          # quality_score <= this counts as "low"
MISROUTE_GAP = 1.0       # a peer must beat the favoured citizen by >= this in mean quality
DEFAULT_MIN_EVIDENCE = 3  # how many settled contracts before a pattern is "recurring"


# ---- helpers ----------------------------------------------------------------

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _by_tag(settled):
    """{tag: [contract, ...]} for settled contracts that carry a quality score."""
    out = {}
    for c in settled:
        if c.get("quality_score") is None:
            continue
        for t in (c.get("required_tags") or []):
            out.setdefault(t, []).append(c)
    return out


# ---- detectors --------------------------------------------------------------
# Each takes (by_tag, min_evidence) and returns a list of proposal dicts.

def _detect_chronic_misroute(by_tag, min_evidence):
    proposals = []
    for tag, rows in by_tag.items():
        by_owner = {}
        for c in rows:
            if c.get("owner"):
                by_owner.setdefault(c["owner"], []).append(c.get("quality_score"))
        means = {o: _mean(qs) for o, qs in by_owner.items() if _mean(qs) is not None}
        if len(means) < 2:
            continue
        recs = [r for r in ((c.get("routing") or {}).get("recommended_by_router") for c in rows) if r]
        if not recs:
            continue
        favoured = max(set(recs), key=recs.count)
        if favoured not in means:
            continue
        best = max(means, key=means.get)
        if best == favoured:
            continue
        if len(by_owner[best]) < min_evidence:
            continue
        if (means[best] - means[favoured]) < MISROUTE_GAP:
            continue
        proposals.append({
            "kind": "chronic-misroute",
            "slug": f"misroute-{tag}",
            "title": f"Re-weight routing for `{tag}` — favoured citizen underperforms",
            "affects": ["_polis/contracts/routing_stats.yml", "_polis/polis.yml"],
            "problem": (f"On `{tag}`, the router most often recommends `{favoured}` "
                        f"(mean quality {means[favoured]:.1f}/5 over {len(by_owner[favoured])} "
                        f"settled), but `{best}` averages {means[best]:.1f}/5 over "
                        f"{len(by_owner[best])}."),
            "evidence_contracts": [c.get("contract_id") for c in rows],
            "metrics": {"tag": tag, "favoured": favoured,
                        "favoured_mean": round(means[favoured], 2),
                        "best_alternative": best, "best_mean": round(means[best], 2)},
            "proposed_change": (f"Raise the per-tag exploration rate for `{tag}` and/or decay "
                                f"`{favoured}`'s self-rating on `{tag}`, so observed outcomes can "
                                f"promote `{best}`."),
            "rationale": ("The bandit is exploiting a stale leader while the evidence shows a peer "
                          "is consistently better; nudging exploration lets the policy self-correct."),
        })
    return proposals


def _detect_recurring_low_quality(by_tag, min_evidence):
    proposals = []
    for tag, rows in by_tag.items():
        if len(rows) < min_evidence:
            continue
        m = _mean([c.get("quality_score") for c in rows])
        if m is None or m > LOW_QUALITY:
            continue
        proposals.append({
            "kind": "recurring-low-quality",
            "slug": f"low-quality-{tag}",
            "title": f"Add a standing acceptance check for `{tag}` work",
            "affects": ["_polis/CONSTITUTION.md"],
            "problem": (f"The last {len(rows)} settled contracts tagged `{tag}` averaged "
                        f"quality {m:.1f}/5 — chronically below bar."),
            "evidence_contracts": [c.get("contract_id") for c in rows],
            "metrics": {"tag": tag, "n": len(rows), "mean_quality": round(m, 2)},
            "proposed_change": (f"Add a constitutional acceptance check every `{tag}` contract must "
                                "satisfy before settlement (a tag-specific checklist or required "
                                "review), and seed a guardrail so it auto-injects into future "
                                f"`{tag}` contracts."),
            "rationale": ("Recurring low quality on a tag is a process gap, not bad luck; a standing "
                          "check raises the floor for whoever takes the work next."),
        })
    return proposals


def _detect_stakes_miscalibration(by_tag, min_evidence):
    proposals = []
    for tag, rows in by_tag.items():
        risky = []
        for c in rows:
            q = c.get("quality_score")
            review = c.get("review") or {}
            high = c.get("stakes") == "high" or review.get("required")
            if q is not None and q <= LOW_QUALITY and not high:
                risky.append(c)
        if len(risky) < min_evidence:
            continue
        proposals.append({
            "kind": "stakes-miscalibration",
            "slug": f"stakes-{tag}",
            "title": f"Default `{tag}` contracts to high stakes (require review)",
            "affects": ["_polis/CONSTITUTION.md"],
            "problem": (f"{len(risky)} `{tag}` contracts settled at quality <= {LOW_QUALITY} without "
                        "being flagged high-stakes or sent to chavruta review."),
            "evidence_contracts": [c.get("contract_id") for c in risky],
            "metrics": {"tag": tag, "n": len(risky)},
            "proposed_change": (f"Treat `{tag}` as high-stakes by default, so a different-vendor "
                                "chavruta review is required before such contracts can settle."),
            "rationale": ("Low-quality work slipping through unreviewed on this tag is a sign the "
                          "stakes rule is miscalibrated for it."),
        })
    return proposals


DETECTORS = (_detect_chronic_misroute, _detect_recurring_low_quality, _detect_stakes_miscalibration)


# ---- amendment writing ------------------------------------------------------

def _amendments_dir(root):
    return root / "amendments" / "proposed"


def _existing_slugs(root):
    """Reflect-slugs already on file (any status), so re-running is idempotent."""
    slugs = set()
    d = _amendments_dir(root)
    if d.exists():
        for f in d.glob("*.md"):
            fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
            if fm and fm.get("reflect_slug"):
                slugs.add(fm["reflect_slug"])
    return slugs


def _render_amendment(p):
    aid = f"{_today()}-{p['slug']}"
    expires = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    fm = {
        "amendment_id": aid,
        "title": p["title"],
        "proposed_by": REFLECTOR,
        "proposed_at": _now(),
        "status": "proposed",
        "kind": p["kind"],
        "reflect_slug": p["slug"],
        "affects": p["affects"],
        "evidence_contracts": p["evidence_contracts"],
        "quorum_required": 1,
        "votes": {"agree": [], "disagree": [], "abstain": [], "request_changes": []},
        "ratified_at": None,
        "expires_at": expires,
    }
    metrics = "\n".join(f"- {k}: {v}" for k, v in p["metrics"].items())
    cites = "\n".join(f"- [[contracts/settled/{c}]]" for c in p["evidence_contracts"])
    body = (
        f"\n# Amendment: {p['title']}\n\n"
        f"> Auto-drafted by `{REFLECTOR}` via `polis reflect` from settled-contract evidence. "
        "Not ratified — citizens vote per the normal amendment flow.\n\n"
        f"## Problem\n{p['problem']}\n\n"
        f"## Evidence\n{metrics}\n\nContracts:\n{cites}\n\n"
        f"## Proposed change\n{p['proposed_change']}\n\n"
        f"## Rationale\n{p['rationale']}\n"
    )
    text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body
    return aid, text


def _append_chronicle(root, aid):
    chron = root / "chronicle.md"
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (f"- {ts} | {REFLECTOR} | proposed amendment | "
            f"[[amendments/proposed/{aid}]] | evidence-mined by polis reflect\n")
    existing = chron.read_text(encoding="utf-8") if chron.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    atomic_write_text(chron, existing + line)


def reflect(polis_root, apply=False, min_evidence=DEFAULT_MIN_EVIDENCE):
    """Mine settled history for process pathologies and return proposed amendments.

    When ``apply`` is True, writes each new proposal to amendments/proposed/ and
    posts a `proposed amendment` chronicle line. Idempotent: a pathology already on
    file (matched by reflect_slug) is reported but not re-written. Never ratifies.
    """
    root = Path(polis_root)
    data = _report.gather(root)
    by_tag = _by_tag(data.get("settled", []))

    proposals = []
    for detect in DETECTORS:
        proposals.extend(detect(by_tag, min_evidence))

    existing = _existing_slugs(root)
    results = []
    for p in proposals:
        already = p["slug"] in existing
        aid, text = _render_amendment(p)
        entry = {
            "amendment_id": aid,
            "kind": p["kind"],
            "title": p["title"],
            "slug": p["slug"],
            "evidence_contracts": p["evidence_contracts"],
            "already_proposed": already,
            "written": False,
        }
        if apply and not already:
            d = _amendments_dir(root)
            d.mkdir(parents=True, exist_ok=True)
            atomic_write_text(d / f"{aid}.md", text)
            _append_chronicle(root, aid)
            entry["written"] = True
        results.append(entry)
    return results
