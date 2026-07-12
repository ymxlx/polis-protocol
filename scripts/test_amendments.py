#!/usr/bin/env python3
"""Tests for the Polis Protocol amendment commands and lifecycle."""

import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import amendments
from polis import doctor
from polis import cli
from polis.routing import parse_frontmatter


def _make_polis(root: Path):
    root.mkdir(parents=True)
    (root / "CONSTITUTION.md").write_text("# constitution\n", encoding="utf-8")
    (root / "chronicle.md").write_text(
        "---\nfile_type: chronicle\n---\n\n- 2026-01-01 00:00 | founder | joined polis | - | -\n",
        encoding="utf-8")
    
    # Register 3 citizens: claude-dev, codex-dev, gemini-dev
    for cid in ("claude-dev", "codex-dev", "gemini-dev"):
        d = root / "citizens" / cid
        d.mkdir(parents=True)
        (d / "capability_card.yml").write_text(
            f"agent_id: {cid}\nvendor: test\ncapability_tags:\n  backend: {{self_rating: 4}}\n",
            encoding="utf-8")
        (d / "status.md").write_text(
            f"---\nagent_id: {cid}\nstate: idle\n---\n",
            encoding="utf-8")


def _write_proposed_amendment(root: Path, aid, title, expires_days=30, quorum=None):
    d = root / "amendments" / "proposed"
    d.mkdir(parents=True, exist_ok=True)
    exp = (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d")
    fm = {
        "amendment_id": aid,
        "title": title,
        "proposed_by": "claude-dev",
        "proposed_at": "2026-07-12 12:00:00",
        "status": "proposed",
        "quorum_required": quorum,
        "votes": {"agree": [], "disagree": [], "abstain": [], "request_changes": []},
        "expires_at": exp,
    }
    import yaml
    content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n# " + title + "\n"
    (d / f"{aid}.md").write_text(content, encoding="utf-8")


class AmendmentsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        _make_polis(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_list_amendments(self):
        _write_proposed_amendment(self.root, "2026-07-12-test-1", "Test Amendment 1")
        # Move one to ratified manually to test list
        rat_dir = self.root / "amendments" / "ratified"
        rat_dir.mkdir(parents=True, exist_ok=True)
        (rat_dir / "2026-07-12-test-2.md").write_text(
            "---\namendment_id: 2026-07-12-test-2\nstatus: ratified\n---\n# Test 2\n",
            encoding="utf-8"
        )
        
        all_amends = amendments.list_amendments(self.root)
        self.assertEqual(len(all_amends), 2)
        ids = [a["amendment_id"] for a in all_amends]
        self.assertIn("2026-07-12-test-1", ids)
        self.assertIn("2026-07-12-test-2", ids)

    def test_vote_amendment(self):
        aid = "2026-07-12-vote-test"
        _write_proposed_amendment(self.root, aid, "Vote Test Amendment")
        
        # Cast a vote
        res = amendments.vote_amendment(self.root, aid, "claude-dev", "agree", rationale="Looks good")
        self.assertTrue(res["ok"])
        self.assertEqual(res["votes"]["agree"], ["claude-dev"])
        
        # Verify markdown file has frontmatter and response block
        f_path = self.root / "amendments" / "proposed" / f"{aid}.md"
        fm, body = parse_frontmatter(f_path.read_text(encoding="utf-8"))
        self.assertEqual(fm["votes"]["agree"], ["claude-dev"])
        self.assertIn("## Response from claude-dev (agree)", body)
        self.assertIn("Looks good", body)
        
        # Verify chronicle got appended
        chron = (self.root / "chronicle.md").read_text(encoding="utf-8")
        self.assertIn("voted on amendment", chron)
        self.assertIn("agree: Looks good", chron)
        
        # Change vote
        res = amendments.vote_amendment(self.root, aid, "claude-dev", "disagree", rationale="Changed my mind")
        self.assertTrue(res["ok"])
        self.assertEqual(res["votes"]["disagree"], ["claude-dev"])
        self.assertEqual(res["votes"]["agree"], [])
        
        fm, body = parse_frontmatter(f_path.read_text(encoding="utf-8"))
        self.assertNotIn("## Response from claude-dev (agree)", body)
        self.assertIn("## Response from claude-dev (disagree)", body)
        self.assertIn("Changed my mind", body)

    def test_vote_validation(self):
        aid = "2026-07-12-vote-val"
        _write_proposed_amendment(self.root, aid, "Vote Val")
        
        with self.assertRaises(ValueError):
            # Invalid vote option
            amendments.vote_amendment(self.root, aid, "claude-dev", "yes-please")
            
        with self.assertRaises(ValueError):
            # Unknown citizen
            amendments.vote_amendment(self.root, aid, "unknown-citizen", "agree")

    def test_tally_active_and_quorum(self):
        # We need to simulate active citizens in the chronicle (last 14 days)
        # Current time is 2026-07-12
        now = datetime(2026, 7, 12, 12, 0, 0)
        
        # Write chronicle lines
        chron_path = self.root / "chronicle.md"
        chron_path.write_text(
            f"- 2026-07-10 10:00 | claude-dev | worked | - | -\n"
            f"- 2026-07-11 11:00 | codex-dev | worked | - | -\n"
            # gemini-dev has no recent lines, so they are inactive
            , encoding="utf-8"
        )
        
        aid = "2026-07-12-tally-ratify"
        # Since active citizens = claude-dev, codex-dev (count 2),
        # Default quorum = max(2, (2 // 2) + 1) = 2.
        _write_proposed_amendment(self.root, aid, "Tally Ratify")
        
        # Only claude-dev votes
        amendments.vote_amendment(self.root, aid, "claude-dev", "agree", now=now)
        
        # Tally - should not ratify yet (only 1 agree, quorum is 2)
        results = amendments.tally_amendments(self.root, now=now)
        self.assertEqual(results, [])
        self.assertTrue((self.root / "amendments" / "proposed" / f"{aid}.md").exists())
        
        # codex-dev votes agree
        amendments.vote_amendment(self.root, aid, "codex-dev", "agree", now=now)
        
        # Tally - should now ratify
        results = amendments.tally_amendments(self.root, now=now)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "ratified")
        
        # Check files moved
        self.assertFalse((self.root / "amendments" / "proposed" / f"{aid}.md").exists())
        self.assertTrue((self.root / "amendments" / "ratified" / f"{aid}.md").exists())
        
        # Check status and chronicle
        fm, _ = parse_frontmatter((self.root / "amendments" / "ratified" / f"{aid}.md").read_text(encoding="utf-8"))
        self.assertEqual(fm["status"], "ratified")
        self.assertIsNotNone(fm["ratified_at"])
        
        chron = (self.root / "chronicle.md").read_text(encoding="utf-8")
        self.assertIn("ratified amendment", chron)

    def test_tally_away_citizen_ignored(self):
        now = datetime(2026, 7, 12, 12, 0, 0)
        # claude-dev and codex-dev both active
        chron_path = self.root / "chronicle.md"
        chron_path.write_text(
            f"- 2026-07-10 10:00 | claude-dev | worked | - | -\n"
            f"- 2026-07-11 11:00 | codex-dev | worked | - | -\n",
            encoding="utf-8"
        )
        # But codex-dev is away!
        (self.root / "citizens" / "codex-dev" / "status.md").write_text(
            "---\nagent_id: codex-dev\nstate: away\n---\n", encoding="utf-8"
        )
        
        aid = "2026-07-12-away-test"
        # Active citizens list should exclude codex-dev, so active = [claude-dev] (count 1)
        # Default quorum should be max(2, (1 // 2) + 1) = 2.
        # Let's set custom quorum_required: 1 in the amendment to test if it can pass
        _write_proposed_amendment(self.root, aid, "Away Test", quorum=1)
        
        amendments.vote_amendment(self.root, aid, "claude-dev", "agree", now=now)
        results = amendments.tally_amendments(self.root, now=now)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "ratified")

    def test_tally_early_rejection(self):
        now = datetime(2026, 7, 12, 12, 0, 0)
        # Active citizens: claude-dev, codex-dev, gemini-dev (count 3)
        # Quorum required: 2
        chron_path = self.root / "chronicle.md"
        chron_path.write_text(
            f"- 2026-07-10 10:00 | claude-dev | worked | - | -\n"
            f"- 2026-07-11 11:00 | codex-dev | worked | - | -\n"
            f"- 2026-07-12 09:00 | gemini-dev | worked | - | -\n",
            encoding="utf-8"
        )
        
        aid = "2026-07-12-reject-test"
        _write_proposed_amendment(self.root, aid, "Reject Test", quorum=2)
        
        # 2 out of 3 citizens vote disagree/abstain/request_changes
        amendments.vote_amendment(self.root, aid, "claude-dev", "disagree", now=now)
        amendments.vote_amendment(self.root, aid, "codex-dev", "disagree", now=now)
        
        # Tally - should reject early because it's impossible to reach quorum of 2 with only 1 potential voter left
        results = amendments.tally_amendments(self.root, now=now)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "rejected")
        
        # Stays in proposed
        f_path = self.root / "amendments" / "proposed" / f"{aid}.md"
        self.assertTrue(f_path.exists())
        fm, _ = parse_frontmatter(f_path.read_text(encoding="utf-8"))
        self.assertEqual(fm["status"], "rejected")

    def test_tally_expiry(self):
        # Current time is 2026-07-12
        now = datetime(2026, 7, 12, 12, 0, 0)
        
        aid = "2026-07-12-expired-test"
        # Expires 2 days ago (-2)
        _write_proposed_amendment(self.root, aid, "Expiry Test", expires_days=-2, quorum=2)
        
        results = amendments.tally_amendments(self.root, now=now)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "expired")
        
        # Stays in proposed but status updated
        f_path = self.root / "amendments" / "proposed" / f"{aid}.md"
        self.assertTrue(f_path.exists())
        fm, _ = parse_frontmatter(f_path.read_text(encoding="utf-8"))
        self.assertEqual(fm["status"], "expired")

    def test_doctor_validation(self):
        aid = "2026-07-12-doctor-test"
        _write_proposed_amendment(self.root, aid, "Doctor Test")
        
        # Clean run
        res = doctor.run_doctor(self.root)
        self.assertTrue(res["ok"])
        
        # Make amendment bad: invalid status
        f_path = self.root / "amendments" / "proposed" / f"{aid}.md"
        fm, body = parse_frontmatter(f_path.read_text(encoding="utf-8"))
        fm["status"] = "something-bad"
        import yaml
        content = "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n" + body
        f_path.write_text(content, encoding="utf-8")
        
        res = doctor.run_doctor(self.root)
        self.assertFalse(res["ok"])
        self.assertTrue(any("invalid status" in err for err in res["errors"]))

    def test_cli_integration(self):
        # We can call the main entry point via sys.argv mock
        aid = "2026-07-12-cli-test"
        _write_proposed_amendment(self.root, aid, "CLI Test")
        
        # Test cli list
        code = cli.main(["amendment", "list", "--polis-root", str(self.root)])
        self.assertEqual(code, 0)
        
        # Test cli vote
        code = cli.main(["amendment", "vote", aid, "--as", "claude-dev", "--vote", "agree", "--rationale", "via cli", "--polis-root", str(self.root)])
        self.assertEqual(code, 0)
        
        # Verify vote registered
        fm, _ = parse_frontmatter((self.root / "amendments" / "proposed" / f"{aid}.md").read_text(encoding="utf-8"))
        self.assertEqual(fm["votes"]["agree"], ["claude-dev"])
        
        # Test cli tally
        # Set quorum to 1 so it ratifies
        fm["quorum_required"] = 1
        import yaml
        (self.root / "amendments" / "proposed" / f"{aid}.md").write_text(
            "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n# CLI Test\n", encoding="utf-8"
        )
        code = cli.main(["amendment", "tally", "--polis-root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertTrue((self.root / "amendments" / "ratified" / f"{aid}.md").exists())


if __name__ == "__main__":
    unittest.main()
