"""Polis Replay — a shareable report of what the team did and learned.

`polis report` renders the polis state (contracts, routing decisions, evidence,
lessons, guardrails) as markdown or a self-contained HTML page. `--redact`
sanitizes it for public sharing: citizen ids become stable anonymous handles and
free-text fields are dropped, so a Replay can be posted without leaking project
detail. Reused by the CLI and the dashboard.
"""
from datetime import datetime
from pathlib import Path

from .routing import load_citizens, load_lessons, load_routing_stats, parse_frontmatter
from . import guardrails as _guardrails
from . import reservations as _reservations


def _contracts(root: Path, state: str) -> list:
    d = root / "contracts" / state
    out = []
    if not d.exists():
        return out
    for f in sorted(d.glob("*.md")):
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm:
            out.append(fm)
    return out


def gather(polis_root) -> dict:
    """Collect everything a Replay needs, in one structure."""
    root = Path(polis_root)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "citizens": load_citizens(root),
        "open": _contracts(root, "open"),
        "settled": _contracts(root, "settled"),
        "abandoned": _contracts(root, "abandoned"),
        "lessons": load_lessons(root),
        "guardrails": _guardrails.list_guardrails(root),
        "reservations": _reservations.active_reservations(root),
        "stats": load_routing_stats(root),
    }


def redact(data: dict) -> dict:
    """Anonymize citizen ids and drop free-text so the Replay is shareable."""
    ids = sorted(set(list(data["citizens"].keys())
                     + [c.get("owner") for c in data["settled"] + data["open"] if c.get("owner")]
                     + [c.get("opened_by") for c in data["settled"] + data["open"] if c.get("opened_by")]))
    alias = {cid: f"agent-{i+1:02d}" for i, cid in enumerate(ids)}

    def a(v):
        return alias.get(v, v)

    out = dict(data)
    out["citizens"] = {a(cid): {"vendor": card.get("vendor", "?")} for cid, card in data["citizens"].items()}
    for key in ("open", "settled", "abandoned"):
        rows = []
        for c in data[key]:
            routing = c.get("routing") or {}
            rows.append({
                "contract_id": c.get("contract_id"),
                "status": c.get("status"),
                "owner": a(c.get("owner")),
                "opened_by": a(c.get("opened_by")),
                "required_tags": c.get("required_tags") or [],
                "quality_score": c.get("quality_score"),
                "actual_minutes": c.get("actual_minutes"),
                "routing": {"recommended_by_router": a(routing.get("recommended_by_router")),
                            "exploration": routing.get("exploration")},
            })
        out[key] = rows
    out["lessons"] = [{"lesson_id": l["lesson_id"],
                       "routing_effect": [{"citizen": a(e.get("citizen")), "tags": e.get("tags"),
                                           "delta": e.get("delta")} for e in l.get("routing_effect", [])]}
                      for l in data["lessons"]]
    out["guardrails"] = [{"guardrail_id": g["guardrail_id"], "tags": g["tags"]} for g in data["guardrails"]]
    out["reservations"] = [{"citizen": a(r.get("citizen")), "paths": ["<redacted>"] * len(r.get("paths", []))}
                           for r in data["reservations"]]
    out["redacted"] = True
    return out


def render_markdown(data: dict) -> str:
    lines = [f"# Polis Replay", f"_generated {data['generated_at']}"
             + (" · redacted for sharing_" if data.get("redacted") else "_"), ""]
    lines += [f"## Citizens ({len(data['citizens'])})"]
    for cid, card in data["citizens"].items():
        vendor = card.get("vendor", "?")
        lines.append(f"- `{cid}` ({vendor})")
    n_open, n_settled = len(data["open"]), len(data["settled"])
    lines += ["", f"## Contracts — {n_settled} settled · {n_open} open · {len(data['abandoned'])} abandoned"]
    for c in data["settled"]:
        q = c.get("quality_score")
        mins = c.get("actual_minutes")
        routing = c.get("routing") or {}
        rec = routing.get("recommended_by_router")
        suffix = f", routed→{rec}" if rec else ""
        lines.append(f"- ✅ `{c.get('contract_id')}` — owner `{c.get('owner')}`, quality {q}"
                     + (f", {mins} min" if mins else "") + suffix)
    for c in data["open"]:
        lines.append(f"- ○ `{c.get('contract_id')}` — {c.get('status')}, owner `{c.get('owner') or '—'}`")
    lines += ["", f"## Lessons with routing effect ({len(data['lessons'])})"]
    for l in data["lessons"]:
        effects = ", ".join(f"{e.get('citizen')} {float(e.get('delta',0)):+g} on {','.join(e.get('tags') or [])}"
                            for e in l.get("routing_effect", []))
        lines.append(f"- `{l['lesson_id']}` → {effects}")
    lines += ["", f"## Guardrails ({len(data['guardrails'])})"]
    for g in data["guardrails"]:
        text = g.get("text", "")
        lines.append(f"- `{g['guardrail_id']}` [{', '.join(g['tags'])}]" + (f": {text}" if text else ""))
    if data["reservations"]:
        lines += ["", f"## Active reservations ({len(data['reservations'])})"]
        for r in data["reservations"]:
            lines.append(f"- `{r.get('citizen')}`: {', '.join(r.get('paths', []))}")
    return "\n".join(lines) + "\n"


def render_html(data: dict) -> str:
    """Self-contained HTML Replay in the telemetry style."""
    import html as _html
    md_body = render_markdown(data)
    rows = "".join(f"<pre>{_html.escape(md_body)}</pre>")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Polis Replay</title><style>
body{{background:#0A0B0D;color:#E7E8E2;font-family:ui-monospace,'JetBrains Mono',monospace;
max-width:880px;margin:0 auto;padding:48px 24px;line-height:1.6}}
pre{{white-space:pre-wrap;border:1px solid rgba(231,232,226,.13);background:#0E1014;padding:24px}}
h1{{letter-spacing:-.02em}}</style></head>
<body><h1>POLIS // REPLAY</h1>{rows}</body></html>"""


def write_report(polis_root, fmt="md", redacted=False, out_path=None) -> str:
    data = gather(polis_root)
    if redacted:
        data = redact(data)
    content = render_html(data) if fmt == "html" else render_markdown(data)
    if out_path is None:
        out_path = Path(polis_root) / ("replay.html" if fmt == "html" else "replay.md")
    from ._io import atomic_write_text
    atomic_write_text(out_path, content)
    return str(out_path)
