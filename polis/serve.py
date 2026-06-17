"""`polis serve` — a local control-plane dashboard for the polis.

Zero dependencies: stdlib http.server reading `_polis/` fresh on every request,
so the page always reflects the current state (refresh to update). Endpoints:

    GET  /                    the dashboard (self-contained HTML, telemetry style)
    GET  /api/state           the full state as JSON (what the extension/MCP reuse)
    GET  /replay.md           the markdown Replay (add ?redact=1 to sanitize)
    POST /api/contract/open   open a contract        (title, required_tags, opened_by, stakes)
    POST /api/contract/claim  claim a contract        (contract_id, citizen)
    POST /api/contract/settle settle a contract       (contract_id, quality, by, minutes)
    POST /api/contract/abandon abandon a contract     (contract_id, reason)
    POST /api/reserve         reserve paths           (citizen, paths, ttl_minutes, note)
    POST /api/release         release reservations    (citizen, paths)

Write actions reuse the same `contracts`/`reservations` functions the CLI and MCP
server call — one shared application layer, no duplicated logic. POST handlers
accept either form-encoded bodies (the no-JS dashboard forms) or JSON (API/extension
callers); form posts 303-redirect back to `/` so the page refreshes.

This server binds to loopback only and assumes trusted local agents (file
reservations are advisory, not security). As defence-in-depth against a browser
being tricked into POSTing to the local port, write requests must carry a
localhost `Host` and, if present, a localhost `Origin`.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote

from . import report as _report
from . import contracts as _contracts
from . import reservations as _reservations


def _state(root) -> dict:
    data = _report.gather(root)
    # citizens dict -> json-friendly summary
    data["citizens"] = {cid: {"vendor": c.get("vendor"), "model": c.get("model"),
                              "tags": sorted((c.get("capability_tags") or {}).keys())}
                        for cid, c in data["citizens"].items()}
    data["lessons"] = [{"lesson_id": l["lesson_id"]} for l in data["lessons"]]
    return data


# ---- write actions ----------------------------------------------------------
# Each handler takes (root, params: dict) and returns (http_status, result: dict).
# They wrap the shared lifecycle functions; the result dict is what JSON callers
# receive and what drives the redirect banner for form posts.

def _csv(value) -> list:
    return [s.strip() for s in (value or "").split(",") if s.strip()]


def _err_status(res: dict) -> int:
    reason = (res.get("reason") or "").lower()
    if "not found" in reason:
        return 404
    if "owned" in reason or res.get("conflicts"):
        return 409
    return 400


def _act_open(root, p):
    title = (p.get("title") or "").strip()
    if not title:
        return 400, {"ok": False, "reason": "title is required"}
    res = _contracts.open_contract(
        root, title, _csv(p.get("required_tags")), p.get("opened_by") or "dashboard",
        stakes=p.get("stakes") or "medium", cost_ceiling=p.get("cost_ceiling") or "medium")
    return 200, {"ok": True, **res}


def _act_claim(root, p):
    res = _contracts.claim_contract(root, p.get("contract_id"), p.get("citizen"),
                                    force=p.get("force") in ("1", "true", "on"))
    return (200 if res.get("ok") else _err_status(res)), res


def _act_settle(root, p):
    res = _contracts.settle_contract(root, p.get("contract_id"), p.get("quality"),
                                     minutes=p.get("minutes") or None, by=p.get("by") or None)
    return (200 if res.get("ok") else _err_status(res)), res


def _act_abandon(root, p):
    res = _contracts.abandon_contract(root, p.get("contract_id"), reason=p.get("reason") or None)
    return (200 if res.get("ok") else _err_status(res)), res


def _act_reserve(root, p):
    citizen, paths = p.get("citizen"), _csv(p.get("paths"))
    if not citizen or not paths:
        return 400, {"ok": False, "reason": "citizen and at least one path are required"}
    ttl = p.get("ttl_minutes")
    res = _reservations.reserve(root, citizen, paths,
                                ttl_minutes=int(ttl) if ttl else None, note=p.get("note") or None)
    return (200 if res.get("ok") else 409), res


def _act_release(root, p):
    citizen = p.get("citizen")
    if not citizen:
        return 400, {"ok": False, "reason": "citizen is required"}
    removed = _reservations.release(root, citizen, paths=_csv(p.get("paths")) or None)
    return 200, {"ok": True, "released": removed}


POST_ACTIONS = {
    "/api/contract/open": _act_open,
    "/api/contract/claim": _act_claim,
    "/api/contract/settle": _act_settle,
    "/api/contract/abandon": _act_abandon,
    "/api/reserve": _act_reserve,
    "/api/release": _act_release,
}


def _dashboard_html(root, msg=None) -> str:
    import html as H
    d = _report.gather(root)
    def esc(x):
        return H.escape(str(x))
    citizen_ids = list(d["citizens"].keys())
    open_ids = [c.get("contract_id") for c in d["open"]]
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
    citizen_opts = "".join(f"<option value=\"{esc(c)}\">" for c in citizen_ids)
    contract_opts = "".join(f"<option value=\"{esc(c)}\">" for c in open_ids)
    banner = f"<div class='banner'>{esc(msg)}</div>" if msg else ""
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
.banner{{margin:20px 0 -6px;padding:10px 14px;background:rgba(232,178,76,.1);border:1px solid var(--gold);color:var(--gold);font-size:12px}}
.acts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1px;background:var(--hair);border:1px solid var(--hair)}}
.acts form{{background:var(--panel);padding:14px 16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.acts form b{{flex-basis:100%;font-size:10px;letter-spacing:.14em;color:var(--gold);text-transform:uppercase}}
.acts input,.acts select{{background:#070809;border:1px solid var(--hair);color:var(--ink);font:inherit;font-size:12px;padding:5px 7px;flex:1;min-width:90px}}
.acts button{{background:var(--cyan);color:#04282b;border:0;font:inherit;font-size:12px;font-weight:700;padding:6px 12px;cursor:pointer}}
</style></head><body>
<header><b>POLIS // CONTROL PLANE</b><span>{esc(d['generated_at'])} · refresh for live state · <a href="/api/state">JSON</a> · <a href="/replay.md">replay</a></span></header>
<main>
{banner}
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
<h2>[ 05 ] Actions</h2>
<datalist id="citizens">{citizen_opts}</datalist>
<datalist id="open">{contract_opts}</datalist>
<div class="acts">
  <form method="post" action="/api/contract/open"><b>Open contract</b>
    <input type="hidden" name="_redirect" value="1">
    <input name="title" placeholder="title" required>
    <input name="required_tags" placeholder="tags (comma)">
    <input name="opened_by" list="citizens" placeholder="opened_by">
    <select name="stakes"><option value="medium">medium</option><option value="high">high</option><option value="low">low</option></select>
    <button>open</button></form>
  <form method="post" action="/api/contract/claim"><b>Claim</b>
    <input type="hidden" name="_redirect" value="1">
    <input name="contract_id" list="open" placeholder="contract_id" required>
    <input name="citizen" list="citizens" placeholder="citizen" required>
    <button>claim</button></form>
  <form method="post" action="/api/contract/settle"><b>Settle</b>
    <input type="hidden" name="_redirect" value="1">
    <input name="contract_id" list="open" placeholder="contract_id" required>
    <input name="quality" type="number" min="1" max="5" placeholder="quality 1-5" required>
    <input name="minutes" type="number" min="0" placeholder="minutes">
    <button>settle</button></form>
  <form method="post" action="/api/reserve"><b>Reserve paths</b>
    <input type="hidden" name="_redirect" value="1">
    <input name="citizen" list="citizens" placeholder="citizen" required>
    <input name="paths" placeholder="paths (comma)" required>
    <input name="ttl_minutes" type="number" min="0" placeholder="ttl min">
    <button>reserve</button></form>
  <form method="post" action="/api/release"><b>Release</b>
    <input type="hidden" name="_redirect" value="1">
    <input name="citizen" list="citizens" placeholder="citizen" required>
    <input name="paths" placeholder="paths (comma, blank=all)">
    <button>release</button></form>
</div>
</main></body></html>"""


def make_handler(polis_root):
    root = Path(polis_root)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: str, ctype: str, status: int = 200):
            payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _local_only(self) -> bool:
            """Reject write requests not clearly from the loopback dashboard
            (defence against DNS-rebinding / cross-site POSTs to the local port)."""
            host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
            if host not in ("127.0.0.1", "localhost", "::1"):
                return False
            origin = self.headers.get("Origin")
            if origin and urlparse(origin).hostname not in ("127.0.0.1", "localhost", "::1"):
                return False
            return True

        def _read_params(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else ""
            ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
            if ctype == "application/json":
                try:
                    obj = json.loads(raw or "{}")
                    return obj if isinstance(obj, dict) else {}
                except json.JSONDecodeError:
                    return {}
            return {k: v[0] for k, v in parse_qs(raw).items()}

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/":
                msg = parse_qs(url.query).get("msg", [None])[0]
                self._send(_dashboard_html(root, msg=msg), "text/html")
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

        def do_POST(self):
            url = urlparse(self.path)
            # Always consume the request body, even on early rejection, so the
            # socket closes cleanly (an unread body triggers a TCP RST → client
            # ConnectionResetError).
            params = self._read_params()
            action = POST_ACTIONS.get(url.path)
            if not action:
                self._send(json.dumps({"ok": False, "reason": "unknown action"}),
                           "application/json", status=404)
                return
            if not self._local_only():
                self._send(json.dumps({"ok": False, "reason": "forbidden: non-local request"}),
                           "application/json", status=403)
                return
            try:
                status, result = action(root, params)
            except Exception as exc:  # bad input from a form/JSON caller
                status, result = 400, {"ok": False, "reason": str(exc)}
            if params.get("_redirect"):
                # No-JS form post: bounce back to the dashboard with a status banner.
                note = "ok" if result.get("ok") else f"error {status}: {result.get('reason') or result.get('conflicts')}"
                self.send_response(303)
                self.send_header("Location", f"/?msg={quote(note)}")
                self.end_headers()
            else:
                self._send(json.dumps(result, default=str), "application/json", status=status)

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
