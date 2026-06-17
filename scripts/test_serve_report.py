#!/usr/bin/env python3
"""Tests for `polis report` (Replay + redaction) and `polis serve` (dashboard)."""
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import guardrails, report, reservations, serve  # noqa: E402
from polis.contracts import claim_contract, open_contract, settle_contract  # noqa: E402


def _make_polis(root: Path):
    root.mkdir(parents=True)
    (root / "CONSTITUTION.md").write_text("# c\n", encoding="utf-8")
    cdir = root / "citizens" / "claude-research-acme"
    cdir.mkdir(parents=True)
    (cdir / "capability_card.yml").write_text(
        "agent_id: claude-research-acme\nvendor: anthropic\n"
        "capability_tags:\n  research: {self_rating: 4}\n", encoding="utf-8")
    cid = open_contract(root, "Secret Acme task", ["research"], "claude-research-acme")["contract_id"]
    claim_contract(root, cid, "claude-research-acme")
    settle_contract(root, cid, quality=4, minutes=30)
    ldir = root / "lessons" / "research"
    ldir.mkdir(parents=True)
    (ldir / "l1.md").write_text(
        "---\nlesson_id: L1\nstatus: accepted\ncapability_tags: [research]\n"
        "routing_effect:\n  - citizen: claude-research-acme\n    tags: [research]\n    delta: 0.05\n---\nbody\n",
        encoding="utf-8")
    guardrails.add_guardrail(root, "Check the sources twice.", ["research"], cid)
    reservations.reserve(root, "claude-research-acme", ["src/secret/path.py"])
    return cid


class ReportTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.cid = _make_polis(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_gather_collects_everything(self):
        d = report.gather(self.root)
        self.assertEqual(len(d["citizens"]), 1)
        self.assertEqual(len(d["settled"]), 1)
        self.assertEqual(len(d["lessons"]), 1)
        self.assertEqual(len(d["guardrails"]), 1)
        self.assertEqual(len(d["reservations"]), 1)

    def test_markdown_replay_mentions_evidence(self):
        md = report.render_markdown(report.gather(self.root))
        self.assertIn("quality 4", md)
        self.assertIn("30 min", md)
        self.assertIn("L1", md)

    def test_redaction_hides_identity_and_paths(self):
        red = report.redact(report.gather(self.root))
        md = report.render_markdown(red)
        self.assertNotIn("claude-research-acme", md)
        self.assertNotIn("src/secret/path.py", md)
        self.assertIn("agent-01", md)
        self.assertIn("redacted", md)

    def test_write_report_html(self):
        path = report.write_report(self.root, fmt="html")
        text = Path(path).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<!DOCTYPE html>"))
        self.assertIn("POLIS // REPLAY", text)


class ServeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        _make_polis(self.root)
        self.httpd = serve.make_server(self.root, port=0)  # ephemeral port
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self._tmp.cleanup()

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=5) as r:
            return r.status, r.read().decode("utf-8")

    def test_dashboard_renders_state(self):
        status, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("POLIS // CONTROL PLANE", body)
        self.assertIn("claude-research-acme", body)
        self.assertIn("GUARDRAILS", body)

    def test_api_state_is_json(self):
        status, body = self._get("/api/state")
        self.assertEqual(status, 200)
        d = json.loads(body)
        self.assertIn("claude-research-acme", d["citizens"])
        self.assertEqual(len(d["settled"]), 1)

    def test_replay_endpoint_redacts(self):
        _, plain = self._get("/replay.md")
        self.assertIn("claude-research-acme", plain)
        _, red = self._get("/replay.md?redact=1")
        self.assertNotIn("claude-research-acme", red)


class ServeActionsTest(unittest.TestCase):
    """POST write-actions: the dashboard as a real control plane, not just a viewer."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.root.mkdir(parents=True)
        (self.root / "CONSTITUTION.md").write_text("# c\n", encoding="utf-8")
        for cid in ("claude-dev-acme", "codex-dev-acme"):
            d = self.root / "citizens" / cid
            d.mkdir(parents=True)
            (d / "capability_card.yml").write_text(
                f"agent_id: {cid}\nvendor: x\ncapability_tags:\n  dev: {{self_rating: 4}}\n",
                encoding="utf-8")
        self.httpd = serve.make_server(self.root, port=0)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self._tmp.cleanup()

    def _post(self, path, data, host="127.0.0.1"):
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=body,
            headers={"Content-Type": "application/json", "Host": host}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8")

    def test_full_lifecycle_via_post(self):
        status, body = self._post("/api/contract/open",
                                  {"title": "Build X", "required_tags": "dev",
                                   "opened_by": "claude-dev-acme"})
        self.assertEqual(status, 200)
        cid = json.loads(body)["contract_id"]
        self.assertEqual(
            self._post("/api/contract/claim", {"contract_id": cid, "citizen": "claude-dev-acme"})[0], 200)
        self.assertEqual(
            self._post("/api/contract/settle", {"contract_id": cid, "quality": "5", "minutes": "12"})[0], 200)
        self.assertTrue(list((self.root / "contracts" / "settled").glob("*.md")))
        self.assertFalse(list((self.root / "contracts" / "open").glob("*.md")))

    def test_reserve_conflict_returns_409(self):
        self.assertEqual(self._post("/api/reserve", {"citizen": "claude-dev-acme", "paths": "src/a.py"})[0], 200)
        status, body = self._post("/api/reserve", {"citizen": "codex-dev-acme", "paths": "src/a.py"})
        self.assertEqual(status, 409)
        self.assertTrue(json.loads(body)["conflicts"])

    def test_claim_already_owned_returns_409(self):
        _, body = self._post("/api/contract/open",
                             {"title": "T", "required_tags": "dev", "opened_by": "claude-dev-acme"})
        cid = json.loads(body)["contract_id"]
        self._post("/api/contract/claim", {"contract_id": cid, "citizen": "claude-dev-acme"})
        self.assertEqual(
            self._post("/api/contract/claim", {"contract_id": cid, "citizen": "codex-dev-acme"})[0], 409)

    def test_settle_missing_contract_returns_404(self):
        self.assertEqual(
            self._post("/api/contract/settle", {"contract_id": "nope", "quality": "3"})[0], 404)

    def test_cross_origin_post_forbidden(self):
        self.assertEqual(self._post("/api/reserve", {"citizen": "x", "paths": "y"}, host="evil.com")[0], 403)

    def test_unknown_action_returns_404(self):
        self.assertEqual(self._post("/api/bogus", {})[0], 404)

    def test_form_post_redirects_to_dashboard(self):
        # A no-JS form post 303-redirects; urllib follows it to GET / (the dashboard).
        body = urllib.parse.urlencode(
            {"citizen": "claude-dev-acme", "paths": "src/x.py", "_redirect": "1"}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/reserve", data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Host": "127.0.0.1"},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            self.assertEqual(r.status, 200)
            self.assertIn("POLIS // CONTROL PLANE", r.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
