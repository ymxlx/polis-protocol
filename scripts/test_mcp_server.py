#!/usr/bin/env python3
"""Tests for `polis mcp` — the MCP server (stdio JSON-RPC) over the polis lifecycle."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from polis import mcp_server  # noqa: E402
from polis.contracts import open_contract  # noqa: E402


def _make_polis(root: Path):
    root.mkdir(parents=True)
    (root / "CONSTITUTION.md").write_text("# The Constitution\n", encoding="utf-8")
    for cid, rating in (("claude-dev", 4), ("codex-dev", 2)):
        cdir = root / "citizens" / cid
        cdir.mkdir(parents=True)
        (cdir / "capability_card.yml").write_text(
            f"agent_id: {cid}\nvendor: test\n"
            f"capability_tags:\n  python: {{self_rating: {rating}}}\n", encoding="utf-8")
    return open_contract(root, "Fix the parser", ["python"], "claude-dev")["contract_id"]


class MCPServerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.cid = _make_polis(self.root)
        self.server = mcp_server.PolisMCPServer(self.root)
        self._next_id = 0

    def tearDown(self):
        self._tmp.cleanup()

    def _rpc(self, method, params=None):
        self._next_id += 1
        return self.server.handle({"jsonrpc": "2.0", "id": self._next_id,
                                   "method": method, "params": params or {}})

    def _call(self, tool, arguments=None):
        resp = self._rpc("tools/call", {"name": tool, "arguments": arguments or {}})
        self.assertNotIn("error", resp, resp)
        result = resp["result"]
        text = result["content"][0]["text"]
        try:
            return result["isError"], json.loads(text)
        except json.JSONDecodeError:
            return result["isError"], text

    # ---- protocol ----

    def test_initialize_negotiates_protocol(self):
        resp = self._rpc("initialize", {"protocolVersion": "2025-03-26",
                                        "capabilities": {}, "clientInfo": {"name": "t"}})
        r = resp["result"]
        self.assertEqual(r["protocolVersion"], "2025-03-26")
        self.assertEqual(r["serverInfo"]["name"], "polis-protocol")
        self.assertIn("tools", r["capabilities"])
        # Unknown client version -> our newest.
        r2 = self._rpc("initialize", {"protocolVersion": "1999-01-01"})["result"]
        self.assertEqual(r2["protocolVersion"], mcp_server.PROTOCOL_VERSIONS[0])

    def test_notifications_get_no_response(self):
        self.assertIsNone(self.server.handle(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method_is_rpc_error(self):
        resp = self._rpc("bogus/method")
        self.assertEqual(resp["error"]["code"], -32601)

    def test_tools_list_matches_handlers(self):
        tools = self._rpc("tools/list")["result"]["tools"]
        names = {t["name"] for t in tools}
        self.assertEqual(names, set(mcp_server.PolisMCPServer._TOOL_HANDLERS.keys()))
        for t in tools:
            self.assertIn("description", t)
            self.assertEqual(t["inputSchema"]["type"], "object")

    # ---- lifecycle through tools ----

    def test_full_lifecycle(self):
        err, status = self._call("polis_status")
        self.assertFalse(err)
        self.assertEqual(status["open_contracts"], 1)
        self.assertEqual(sorted(status["citizens"]), ["claude-dev", "codex-dev"])

        err, route = self._call("polis_route", {"contract_id": self.cid, "seed": 1})
        self.assertFalse(err)
        self.assertIn(route["recommendation"], ("claude-dev", "codex-dev"))
        self.assertEqual(len(route["scores"]), 2)

        err, packet = self._call("polis_context", {"contract_id": self.cid})
        self.assertFalse(err)
        self.assertIn("Context packet", packet["markdown"])

        err, claim = self._call("polis_claim_contract",
                                {"contract_id": self.cid, "citizen": "claude-dev"})
        self.assertFalse(err)
        self.assertEqual(claim["owner"], "claude-dev")

        err, settle = self._call("polis_settle_contract",
                                 {"contract_id": self.cid, "quality": 5, "minutes": 12})
        self.assertFalse(err)
        self.assertEqual(settle["quality_score"], 5)

        err, listed = self._call("polis_list_contracts", {"state": "settled"})
        self.assertFalse(err)
        self.assertEqual(len(listed["contracts"]), 1)

    def test_open_contract_inherits_guardrail(self):
        err, _ = self._call("polis_add_guardrail",
                            {"text": "Run the full test suite.", "tags": ["python"]})
        self.assertFalse(err)
        err, opened = self._call("polis_open_contract",
                                 {"title": "Another python task", "required_tags": ["python"],
                                  "opened_by": "claude-dev"})
        self.assertFalse(err)
        text = Path(opened["path"]).read_text(encoding="utf-8")
        self.assertIn("[guardrail] Run the full test suite.", text)

    def test_reservation_conflict_is_tool_error(self):
        err, res = self._call("polis_reserve",
                              {"citizen": "claude-dev", "paths": ["src/app.py"]})
        self.assertFalse(err)
        err, _ = self._call("polis_reserve",
                            {"citizen": "codex-dev", "paths": ["src/app.py"]})
        self.assertTrue(err)  # collision rejected, surfaced as isError
        err, rel = self._call("polis_release", {"citizen": "claude-dev"})
        self.assertFalse(err)
        self.assertEqual(rel["released"], 1)
        err, active = self._call("polis_reservations")
        self.assertFalse(err)
        self.assertEqual(active["reservations"], [])

    def test_unknown_tool_and_missing_args(self):
        resp = self._rpc("tools/call", {"name": "polis_nope", "arguments": {}})
        self.assertEqual(resp["error"]["code"], -32602)
        err, msg = self._call("polis_route", {})  # contract_id missing
        self.assertTrue(err)
        self.assertIn("contract_id", msg)
        err, msg = self._call("polis_route", {"contract_id": "ghost"})
        self.assertTrue(err)
        self.assertIn("not found", msg)

    # ---- resources ----

    def test_resources_list_and_read(self):
        uris = {r["uri"] for r in self._rpc("resources/list")["result"]["resources"]}
        self.assertEqual(uris, {"polis://state", "polis://replay",
                                "polis://replay/redacted", "polis://constitution"})
        state = self._rpc("resources/read", {"uri": "polis://state"})["result"]
        d = json.loads(state["contents"][0]["text"])
        self.assertIn("claude-dev", d["citizens"])
        replay = self._rpc("resources/read", {"uri": "polis://replay"})["result"]
        self.assertIn("Polis Replay", replay["contents"][0]["text"])
        red = self._rpc("resources/read", {"uri": "polis://replay/redacted"})["result"]
        self.assertNotIn("claude-dev", red["contents"][0]["text"])
        con = self._rpc("resources/read", {"uri": "polis://constitution"})["result"]
        self.assertIn("Constitution", con["contents"][0]["text"])
        resp = self._rpc("resources/read", {"uri": "polis://nope"})
        self.assertEqual(resp["error"]["code"], -32002)


class StdioTransportTest(unittest.TestCase):
    """One real round-trip through `python -m polis.mcp_server` over stdio."""

    def test_stdio_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "_polis"
            _make_polis(root)
            msgs = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                            "clientInfo": {"name": "test", "version": "0"}}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                "this is not json",
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                 "params": {"name": "polis_status", "arguments": {}}},
            ]
            stdin = "\n".join(m if isinstance(m, str) else json.dumps(m) for m in msgs) + "\n"
            env = dict(os.environ, PYTHONPATH=str(REPO))
            proc = subprocess.run(
                [sys.executable, "-m", "polis.mcp_server", "--polis-root", str(root)],
                input=stdin, capture_output=True, text=True, timeout=30, env=env, cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
            by_id = {l.get("id"): l for l in lines}
            self.assertEqual(by_id[1]["result"]["serverInfo"]["name"], "polis-protocol")
            self.assertTrue(by_id[2]["result"]["tools"])
            self.assertEqual(by_id[None]["error"]["code"], -32700)  # the non-JSON line
            status = json.loads(by_id[3]["result"]["content"][0]["text"])
            self.assertEqual(status["open_contracts"], 1)


if __name__ == "__main__":
    unittest.main()
