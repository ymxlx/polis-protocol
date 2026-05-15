# Examples

Worked polises showing the protocol applied to real-world team shapes. Each example is a frozen snapshot — the chronicle, contracts, lessons, and routing stats are realistic but not live.

| Example | Status | Team shape | What it shows |
|---|---|---|---|
| [`research-team/`](research-team/) | ✅ shipped | 1 Claude (research) + 1 Codex (frontend) + 1 Gemini (translation) | Cross-vendor routing, a chavruta review on a high-stakes call, an amendment that changed the lesson-filing threshold, a settled contract with a routing-shifting lesson |
| `product-team/` | 🟡 PRs welcome | 2 Claude sessions (designer + writer) + 1 Codex (engineer) + 1 GPT (reviewer) | Same-vendor multiplicity, a stalled contract reassigned, a lesson that flipped the leader on a tag |
| `oss-maintainer/` | 🟡 PRs welcome | 1 Claude (triage) + 1 Codex (patches) + 1 Gemini (release notes) | Quarterly chronicle rollover, an expired amendment, a silent citizen with contracts transferred |

The `research-team` example is a full `_polis/` you can read end-to-end. Open `_polis/index.md` first, scan `_polis/chronicle.md`, then drill into any contract or lesson.

## How to use these

- **Reading**: open in your favorite Markdown viewer or Obsidian (each example is a valid Obsidian vault).
- **Forking**: copy a folder to bootstrap your own polis. Then run `python3 ../../scripts/init_polis.py --force ...` against your project root to refresh the bridge pointers.
- **Routing experiments**: `python3 ../../scripts/route_contract.py --polis-root research-team/_polis --reconcile` rebuilds the stats from settled contracts so you can see the bandit's view.

Got a team shape that isn't covered? PRs welcome — one folder per worked example, with a short README at the top explaining what makes the shape distinctive.
