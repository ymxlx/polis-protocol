#!/usr/bin/env python3
"""
route_contract.py — recommend a citizen for an open contract using the bandit policy.

Reads the polis state (capability cards and routing_stats.yml), scores every
registered citizen against the contract's required_tags, and prints a
recommendation. The user (or the contract opener) makes the final call.

Usage:
    python route_contract.py --polis-root <path> --contract <path-to-contract.md>

Optional:
    --explain                 # print the score breakdown for every citizen
    --apply                   # write the recommendation into the contract's routing.recommended_by_router field
    --adaptive                # use adaptive explore_rate per-tag based on leader_confidence
    --reconcile               # rebuild routing_stats.yml from settled contracts; ignores --contract

The recommendation is a starting point. Any citizen can claim against the router
by editing the contract's owner field and noting routing.override.
"""

import argparse
import math
import random
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "This script needs PyYAML. Install with: pip install pyyaml\n"
        "Or run the routing logic by hand using the formulas in references/routing.md.\n"
    )
    sys.exit(1)


WEIGHTS_DEFAULT = {
    "history": 0.55,
    "self": 0.20,
    "cost": 0.15,
    "avail": 0.10,
}

# Accepted lessons can nudge routing, but never dominate it: the summed effect
# applied to any one citizen for a contract is clamped to +/- LESSON_CAP.
LESSON_CAP = 0.15

COST_FIT = {
    # cost_ceiling -> citizen.cost_envelope.relative -> score
    ("low", "low"): 1.0,
    ("low", "medium"): 0.5,
    ("low", "high"): 0.0,
    ("medium", "low"): 1.0,
    ("medium", "medium"): 1.0,
    ("medium", "high"): 0.5,
    ("high", "low"): 1.0,
    ("high", "medium"): 1.0,
    ("high", "high"): 1.0,
}


def parse_frontmatter(text: str) -> tuple:
    """Return (frontmatter_dict, body_str). Frontmatter is the YAML block at the top."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def load_citizens(polis_root: Path) -> dict:
    """Return dict of agent_id -> capability_card_dict for every registered citizen."""
    citizens = {}
    citizens_dir = polis_root / "citizens"
    if not citizens_dir.exists():
        return citizens
    for agent_dir in citizens_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        card_path = agent_dir / "capability_card.yml"
        if not card_path.exists():
            continue
        try:
            card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"  warning: could not parse {card_path}: {e}")
            continue
        if card and card.get("agent_id"):
            citizens[card["agent_id"]] = card
    return citizens


def load_routing_stats(polis_root: Path) -> dict:
    """Return the routing stats dict; empty if not yet initialized."""
    stats_path = polis_root / "contracts" / "routing_stats.yml"
    if not stats_path.exists():
        return {"explore_rate": 0.15, "tags": {}}
    return yaml.safe_load(stats_path.read_text(encoding="utf-8")) or {"explore_rate": 0.15, "tags": {}}


def load_lessons(polis_root: Path) -> list:
    """Return accepted lessons that declare a structured routing_effect.

    A lesson influences routing only if it is accepted (``status: accepted`` or
    no status field at all) and carries a ``routing_effect`` list of
    ``{citizen, tags, delta}`` entries. Lessons without ``routing_effect`` are
    advisory prose only and never change scores.
    """
    lessons = []
    lessons_dir = polis_root / "lessons"
    if not lessons_dir.exists():
        return lessons
    for path in sorted(lessons_dir.rglob("*.md")):
        try:
            fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not fm:
            continue
        if str(fm.get("status", "accepted")).lower() != "accepted":
            continue
        effects = fm.get("routing_effect")
        if not isinstance(effects, list):
            continue
        lessons.append({
            "lesson_id": fm.get("lesson_id", path.stem),
            "routing_effect": effects,
        })
    return lessons


def lessons_score(citizen_id: str, required_tags: list, lessons: list) -> tuple:
    """Return (bounded_bonus, [applied_lesson_ids]) for a citizen on these tags.

    Each routing_effect entry adds its ``delta`` when its ``citizen`` matches and
    its ``tags`` intersect the contract's required_tags (an empty/omitted tag
    list means "applies to any tag"). The summed bonus is clamped to
    +/- ``LESSON_CAP`` so lessons nudge rather than override the base score.
    """
    if not required_tags or not lessons:
        return 0.0, []
    req = set(required_tags)
    raw = 0.0
    applied = []
    for lesson in lessons:
        for effect in lesson.get("routing_effect", []) or []:
            if effect.get("citizen") != citizen_id:
                continue
            effect_tags = set(effect.get("tags", []) or [])
            if effect_tags and not (effect_tags & req):
                continue
            try:
                delta = float(effect.get("delta", 0.0))
            except (TypeError, ValueError):
                continue
            if delta == 0.0:
                continue
            raw += delta
            applied.append(lesson["lesson_id"])
    bonus = max(-LESSON_CAP, min(LESSON_CAP, raw))
    return bonus, applied


def load_citizen_status(polis_root: Path, agent_id: str) -> dict:
    """Return parsed status frontmatter for a citizen, or empty dict."""
    path = polis_root / "citizens" / agent_id / "status.md"
    if not path.exists():
        return {}
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    return fm or {}


def confidence_factor(n: int) -> float:
    """Rises with sample size. n=0 -> 0; n=3 -> 0.5; n=10 -> 0.77."""
    if n <= 0:
        return 0.0
    return 1 - 1 / (1 + n / 3)


def historical_score(citizen_id: str, required_tags: list, stats: dict) -> float:
    """Mean of per-tag historical scores, each weighted by confidence."""
    if not required_tags:
        return 0.0
    total = 0.0
    for tag in required_tags:
        tag_stats = stats.get("tags", {}).get(tag, {}).get("citizens", {}).get(citizen_id)
        if not tag_stats:
            continue
        avg_q = tag_stats.get("avg_quality_score", 0.0)
        n = tag_stats.get("contracts_completed", 0)
        total += (avg_q / 5.0) * confidence_factor(n)
    return total / len(required_tags)


def self_rating_score(card: dict, required_tags: list) -> float:
    """Mean of per-tag self-ratings (normalized 0-1)."""
    if not required_tags:
        return 0.0
    tags = card.get("capability_tags", {}) or {}
    total = 0.0
    for tag in required_tags:
        entry = tags.get(tag)
        if not entry:
            continue
        total += entry.get("self_rating", 0) / 5.0
    return total / len(required_tags)


def cost_fit_score(card: dict, contract_ceiling: str) -> float:
    citizen_cost = (card.get("cost_envelope") or {}).get("relative", "medium")
    return COST_FIT.get((contract_ceiling, citizen_cost), 0.5)


def availability_score(status: dict) -> float:
    state = status.get("state", "idle")
    if state == "idle":
        return 1.0
    if state == "working":
        if status.get("blockers"):
            return 0.5
        return 0.7
    if state in ("blocked", "reviewing"):
        return 0.3
    if state == "away":
        return 0.0
    return 0.5


def score_citizen(citizen_id: str, card: dict, status: dict, contract: dict, stats: dict, weights: dict, lessons: list = None) -> dict:
    required_tags = contract.get("required_tags") or []
    cost_ceiling = contract.get("cost_ceiling", "medium")

    h = historical_score(citizen_id, required_tags, stats)
    s = self_rating_score(card, required_tags)
    c = cost_fit_score(card, cost_ceiling)
    a = availability_score(status)
    lesson_bonus, applied_lessons = lessons_score(citizen_id, required_tags, lessons or [])

    base = weights["history"] * h + weights["self"] * s + weights["cost"] * c + weights["avail"] * a
    total = base + lesson_bonus

    return {
        "citizen": citizen_id,
        "historical": h,
        "self_rating": s,
        "cost_fit": c,
        "availability": a,
        "lessons": lesson_bonus,
        "applied_lessons": applied_lessons,
        "total": total,
    }


def adaptive_explore_rate(base_rate: float, leader_confidence: float, adjustment: float = 0.2) -> float:
    return min(0.5, base_rate + (1 - leader_confidence) * adjustment)


def pick_recommendation(scores: list, explore_rate: float, rng: random.Random) -> tuple:
    """Return (chosen_citizen_id, exploration_bool, score_of_choice)."""
    if not scores:
        return None, False, 0.0
    scores_sorted = sorted(scores, key=lambda s: s["total"], reverse=True)
    if len(scores_sorted) == 1:
        return scores_sorted[0]["citizen"], False, scores_sorted[0]["total"]
    if rng.random() < explore_rate:
        # Explore: pick from non-leaders, weighted by score (clamp >=0).
        candidates = scores_sorted[1:]
        weights = [max(s["total"], 0.0001) for s in candidates]
        total_w = sum(weights)
        r = rng.uniform(0, total_w)
        upto = 0
        for cand, w in zip(candidates, weights):
            upto += w
            if upto >= r:
                return cand["citizen"], True, cand["total"]
        return candidates[-1]["citizen"], True, candidates[-1]["total"]
    # Exploit.
    return scores_sorted[0]["citizen"], False, scores_sorted[0]["total"]


def _extract_quality(fm: dict, body: str) -> int:
    """Return the contract's quality self-score (1-5).

    Resolution order:
      1. Frontmatter `quality_score` field, if present and an int.
      2. Body line of the form `Quality self-score: N` anchored to start-of-line
         (optionally after a markdown heading marker like `### `).
      3. Body pattern `### Quality self-score\n\nN` (heading then blank line then
         the number alone on its own line) — the historical layout.
      4. Default of 3 if nothing matches.

    Anchoring to start-of-line (`^` with re.MULTILINE) prevents stray digits
    inside prose ("scored 5/5 in usability") from being captured.
    """
    if isinstance(fm.get("quality_score"), int):
        return max(1, min(5, fm["quality_score"]))
    m = re.search(
        r"^\s*(?:#{1,6}\s*)?Quality\s*self[-_ ]score\s*:\s*(\d+)\s*$",
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    if m:
        return int(m.group(1))
    m = re.search(
        r"^\s*#{1,6}\s*Quality\s*self[-_ ]score\s*$\s*\n\s*\n\s*(\d+)\s*$",
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    return int(m.group(1)) if m else 3


def _extract_actual_minutes(fm: dict, body: str) -> int:
    """Return actual minutes spent on the contract.

    Resolution order:
      1. Frontmatter `actual_minutes` field, if present and an int.
      2. Body line of the form `actual_minutes: N` (or `actual minutes: N`)
         anchored to start-of-line, optionally after a markdown heading or
         list marker.
      3. Default of 30 if nothing matches.

    The label MUST appear at the start of its own line and be followed by a
    colon. This deliberately ignores prose mentions like "6 actual_minutes per
    paper × 12 papers", which would otherwise win because `re.search` returns
    the first match and grabs the nearest digit.
    """
    if isinstance(fm.get("actual_minutes"), int):
        return max(1, fm["actual_minutes"])
    m = re.search(
        r"^\s*(?:#{1,6}\s*|[-*]\s+)?actual[_ ]minutes\s*:\s*(\d+)\s*$",
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    return int(m.group(1)) if m else 30


def reconcile_stats(polis_root: Path) -> None:
    """Rebuild routing_stats.yml from scratch by replaying settled contracts."""
    settled_dir = polis_root / "contracts" / "settled"
    if not settled_dir.exists():
        print("No settled contracts directory; nothing to reconcile.")
        return

    tag_data: dict = {}
    settlements = []
    for path in settled_dir.glob("*.md"):
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm or fm.get("status") != "settled":
            continue
        owner = fm.get("owner")
        required_tags = fm.get("required_tags") or []
        settled_at = fm.get("settled_at") or fm.get("opened_at")
        quality = _extract_quality(fm, body)
        actual_minutes = _extract_actual_minutes(fm, body)
        settlements.append((settled_at, owner, required_tags, quality, actual_minutes))

    settlements.sort()  # by settled_at

    for settled_at, owner, required_tags, quality, actual_minutes in settlements:
        for tag in required_tags:
            tag_data.setdefault(tag, {"citizens": {}})
            citizens = tag_data[tag]["citizens"]
            citizens.setdefault(owner, {
                "contracts_completed": 0,
                "avg_quality_score": 0.0,
                "avg_actual_minutes": 0.0,
                "last_completed": None,
            })
            c = citizens[owner]
            n = c["contracts_completed"]
            c["avg_quality_score"] = (c["avg_quality_score"] * n + quality) / (n + 1)
            c["avg_actual_minutes"] = (c["avg_actual_minutes"] * n + actual_minutes) / (n + 1)
            c["contracts_completed"] = n + 1
            c["last_completed"] = str(settled_at)[:10] if settled_at else None

    # Compute leaders and confidence.
    for tag, td in tag_data.items():
        citizens = td["citizens"]
        if not citizens:
            continue
        sorted_c = sorted(citizens.items(), key=lambda kv: kv[1]["avg_quality_score"], reverse=True)
        td["leader"] = sorted_c[0][0]
        if len(sorted_c) >= 2:
            gap = sorted_c[0][1]["avg_quality_score"] - sorted_c[1][1]["avg_quality_score"]
        else:
            gap = sorted_c[0][1]["avg_quality_score"] / 5.0
        total_n = sum(c["contracts_completed"] for c in citizens.values())
        confidence = 1 / (1 + math.exp(-(gap * math.sqrt(total_n) / 3)))
        td["leader_confidence"] = round(confidence, 3)

    import datetime
    out = {
        "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "explore_rate": 0.15,
        "tags": tag_data,
    }
    stats_path = polis_root / "contracts" / "routing_stats.yml"
    stats_path.write_text(yaml.dump(out, default_flow_style=False, sort_keys=False), encoding="utf-8")
    print(f"Reconciled {len(settlements)} settlements into {stats_path}.")


def main():
    parser = argparse.ArgumentParser(description="Recommend a citizen for an open contract.")
    parser.add_argument("--polis-root", required=True, help="Path to the _polis/ folder.")
    parser.add_argument("--contract", help="Path to the open contract .md file.")
    parser.add_argument("--explain", action="store_true", help="Print score breakdown for every citizen.")
    parser.add_argument("--apply", action="store_true", help="Write the recommendation into the contract.")
    parser.add_argument("--adaptive", action="store_true", help="Use adaptive explore_rate per-tag.")
    parser.add_argument("--reconcile", action="store_true", help="Rebuild routing_stats.yml from settled contracts.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible exploration.")
    args = parser.parse_args()

    polis_root = Path(args.polis_root).resolve()
    if not polis_root.exists():
        raise SystemExit(f"Polis root not found: {polis_root}")

    if args.reconcile:
        reconcile_stats(polis_root)
        return

    if not args.contract:
        raise SystemExit("--contract is required unless --reconcile is set.")

    contract_path = Path(args.contract).resolve()
    if not contract_path.exists():
        raise SystemExit(f"Contract not found: {contract_path}")

    contract_fm, contract_body = parse_frontmatter(contract_path.read_text(encoding="utf-8"))
    if not contract_fm:
        raise SystemExit("Contract file has no YAML frontmatter; cannot route.")

    citizens = load_citizens(polis_root)
    if not citizens:
        raise SystemExit("No registered citizens found; nothing to route to.")

    stats = load_routing_stats(polis_root)
    lessons = load_lessons(polis_root)
    explore_rate = stats.get("explore_rate", 0.15)

    # Schema v2: prefer routing policy from _polis/polis.yml when present.
    weights = WEIGHTS_DEFAULT
    from . import config as _config
    if _config.has_config(polis_root):
        _cfg = _config.load_config(polis_root)
        _routing_cfg = _cfg.get("routing", {}) or {}
        weights = _routing_cfg.get("weights", WEIGHTS_DEFAULT)
        explore_rate = _routing_cfg.get("explore_rate", explore_rate)

    if args.adaptive:
        # Use the lowest leader_confidence across required tags to widen exploration.
        required_tags = contract_fm.get("required_tags") or []
        confidences = [stats.get("tags", {}).get(t, {}).get("leader_confidence", 0.0) for t in required_tags]
        min_conf = min(confidences) if confidences else 0.0
        explore_rate = adaptive_explore_rate(explore_rate, min_conf)

    scores = []
    for cid, card in citizens.items():
        status = load_citizen_status(polis_root, cid)
        scores.append(score_citizen(cid, card, status, contract_fm, stats, weights, lessons))

    rng = random.Random(args.seed)
    chosen, is_exploration, chosen_score = pick_recommendation(scores, explore_rate, rng)

    if args.explain:
        print("\nScore breakdown (sorted by total):")
        for s in sorted(scores, key=lambda x: x["total"], reverse=True):
            print(f"  {s['citizen']:30s}  total={s['total']:.3f}  "
                  f"hist={s['historical']:.2f}  self={s['self_rating']:.2f}  "
                  f"cost={s['cost_fit']:.2f}  avail={s['availability']:.2f}  "
                  f"lessons={s.get('lessons', 0.0):+.2f}")
            if s.get("applied_lessons"):
                print(f"  {'':30s}    ↳ lessons applied: {', '.join(s['applied_lessons'])}")
        print(f"\nExplore rate: {explore_rate:.2f}")

    print(f"\nRecommendation: {chosen}")
    print(f"  Score: {chosen_score:.3f}")
    print(f"  Exploration pick: {is_exploration}")

    if args.apply:
        import re as re_mod
        text = contract_path.read_text(encoding="utf-8")
        # Replace the routing block in frontmatter.
        text = re_mod.sub(
            r"(routing:\s*\n)(\s*recommended_by_router:.*?\n\s*recommendation_score:.*?\n\s*exploration:.*?\n)",
            f"\\1  recommended_by_router: {chosen}\n  recommendation_score: {chosen_score:.3f}\n  exploration: {str(is_exploration).lower()}\n",
            text,
            flags=re_mod.DOTALL,
        )
        contract_path.write_text(text, encoding="utf-8")
        print(f"  Applied to {contract_path}")


if __name__ == "__main__":
    main()
