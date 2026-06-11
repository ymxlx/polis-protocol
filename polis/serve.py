"""`polis serve` — a local, read-only dashboard for the polis.

Zero dependencies: stdlib http.server reading `_polis/` fresh on every request,
so the page always reflects the current state (refresh to update). Endpoints:

    GET /            the dashboard (self-contained HTML, telemetry style)
    GET /api/state   the full state as JSON (what the extension/MCP will reuse)
    GET /replay.md   the markdown Replay (add ?redact=1 to sanitize)

Write actions (open/claim/settle from the UI) are a later increment; the CLI
covers them today.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from . import report as _report


def _state(root) -> dict:
    data = _report.gather(root)
    # citizens dict -> json-friendly summary
    data["citizens"] = {cid: {"vendor": c.get("vendor"), "model": c.get("model"),
                              "tags": sorted((c.get("capability_tags") or {}).keys())}
                        for cid, c in data["citizens"].items()}
    data["lessons"] = [{"lesson_id": l["lesson_id"]} for l in data["lessons"]]
    return data


def _dashboard_html(root) -> str:
    import html as H
    d = _report.gather(root)
    def esc(x):
        return H.escape(str(x))
    citizens = "".join(
        f"<tr><td>{esc(cid)}</td><td>{esc(c.get('vendor','?'))}</td>"
        f"<td>{esc(', '.join(sorted((c.get('capability_tags') or {}).keys())))}</td></tr>"
        for cid, c in d["citizens"].items()) or "<tr><td colspan=3>none</td></tr>"
    def crow(c, mark):
        routing = c.get("routing") or {}
        return (f"<tr><td>{mark}</td><td>{esc(c.get('contract_id'))}</td>"
                f"<td>{esc(c.get('owner') or '—')}</td>"
                f"<td>{esc(', '.join(c.get('required_tags') or []))}</td>"
                f"<td>{esc(c.get('quality_score') if c.get('quality_score') is not None else '')}</td>"
                f"<td>{esc(routing.get('recommended_by_router') or '')}</td></tr>")
    contracts = "".join([crow(c, "○") for c in d["open"]] + [crow(c, "✓") for c in d["settled"]]) \
        or "<tr><td colspan=6>none</td></tr>"
    reservations = "".join(
        f"<tr><td>{esc(r.get('citizen'))}</td><td>{esc(', '.join(r.get('paths', [])))}</td>"
        f"<td>{esc(r.get('expires_at') or 'no expiry')}</td></tr>"
        for r in d["reservations"]) or "<tr><td colspan=3>none</td></tr>"
    guardrails = "".join(
        f"<tr><td>{esc(g['guardrail_id'])}</td><td>{esc(', '.join(g['tags']))}</td><td>{esc(g.get('text',''))}</td></tr>"
        for g in d["guardrails"]) or "<tr><td colspan=3>none</td></tr>"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>POLIS // CONTROL PLANE</title>
<style>
:root{{--bg:#0A0B0D;--panel:#0E1014;--ink:#E7E8E2;--mut:#8C8E86;--gold:#E8B24C;--cyan:#46cfdb;--hair:rgba(231,232,226,.13)}}
body{{background:var(--bg);color:var(--ink);font-family:ui-monospace,'JetBrains Mono',monospace;margin:0;padding:0 0 60px;line-height:1.55}}
header{{border-bottom:1px solid var(--hair);padding:14px 26px;display:flex;justify-content:space-between;align-items:center}}
header b{{letter-spacing:.04em}} header span{{color:var(--mut);font-size:11px;letter-spacing:.12em}}
main{{max-width:1080px;margin:0 auto;padding:0 26px}}
h2{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);border-bottom:1px solid var(--hair);padding:26px 0 10px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td,th{{border-top:1px solid rgba(231,232,226,.07);padding:7px 10px 7px 0;text-align:left;color:var(--mut);vertical-align:top}}
td:first-child{{color:var(--ink)}}
.kpis{{display:flex;gap:1px;background:var(--hair);border:1px solid var(--hair);margin-top:26px}}
.kpis div{{flex:1;background:var(--panel);padding:16px;text-align:center}}
.kpis b{{display:block;font-size:26px;color:var(--cyan)}} .kpis span{{font-size:10px;letter-spacing:.14em;color:var(--mut)}}
a{{color:var(--cyan)}}
</style></head><body>
<header><b>POLIS // CONTROL PLANE</b><span>{esc(d['generated_at'])} · refresh for live state · <a href="/api/state">JSON</a> · <a href="/replay.md">replay</a></span></header>
<main>
<div class="kpis">
  <div><b>{len(d['citizens'])}</b><span>CITIZENS</span></div>
  <div><b>{len(d['open'])}</b><span>OPEN</span></div>
  <div><b>{len(d['settled'])}</b><span>SETTLED</span></div>
  <div><b>{len(d['lessons'])}</b><span>ROUTING LESSONS</span></div>
  <div><b>{len(d['guardrails'])}</b><span>GUARDRAILS</span></div>
  <div><b>{len(d['reservations'])}</b><span>RESERVATIONS</span></div>
</div>
<h2>[ 01 ] Citizens</h2><table>{citizens}</table>
<h2>[ 02 ] Contracts</h2><table><tr><th></th><th>id</th><th>owner</th><th>tags</th><th>quality</th><th>routed→</th></tr>{contracts}</table>
<h2>[ 03 ] Active reservations</h2><table>{reservations}</table>
<h2>[ 04 ] Guardrails</h2><table>{guardrails}</table>
</main></body></html>"""


def make_handler(polis_root):
    root = Path(polis_root)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: str, ctype: str):
            payload = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/":
                self._send(_dashboard_html(root), "text/html")
            elif url.path == "/api/state":
                self._send(json.dumps(_state(root), default=str), "application/json")
            elif url.path == "/replay.md":
                redacted = parse_qs(url.query).get("redact", ["0"])[0] == "1"
                data = _report.gather(root)
                if redacted:
                    data = _report.redact(data)
                self._send(_report.render_markdown(data), "text/markdown")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *args):  # quiet
            pass

    return Handler


def make_server(polis_root, port=7341):
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(polis_root))


def serve(polis_root, port=7341):
    httpd = make_server(polis_root, port)
    print(f"polis serve — dashboard at http://127.0.0.1:{port}  (Ctrl-C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
