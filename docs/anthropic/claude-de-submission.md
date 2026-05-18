# clau.de plugin directory — submission package

**Form URLs (submit to BOTH for redundancy):**
- Primary: https://clau.de/plugin-directory-submission
- Console mirror: https://platform.claude.com/plugins/submit

Anthropic auto-rejected the direct PR ([anthropics/claude-plugins-official#1893](https://github.com/anthropics/claude-plugins-official/pull/1893)) and explicitly pointed to these forms. This is the canonical channel.

---

## Copy-paste fields

### Plugin name
```
polis-protocol
```

### Plugin URL / Repository
```
https://github.com/yehudalevy-collab/polis-protocol
```

### Author / Maintainer
```
Yehuda Levy
```

### Author GitHub
```
yehudalevy-collab
```

### Contact email
```
yehuda.moshe24@gmail.com
```

### License
```
MIT
```

### Category (pick the closest)
```
agents
```
**Fallback options if "agents" not present:** `workflow` → `coordination` → `development`

### Tags (comma-separated)
```
multi-agent, coordination, orchestration, markdown, bandit-routing, governance, vendor-agnostic, claude-code, codex, gemini
```

### Short description (1 sentence, ≤120 chars)
```
Markdown coordination protocol for multi-vendor AI agent teams — capability cards, bandit routing, self-amending constitution.
```

### Long description (≤200 words)
```
Polis Protocol is a markdown-only coordination layer for teams of AI agents working on the same project across different vendors (Claude Code, Codex, Gemini CLI, and anything else that reads markdown).

Three primitives form the protocol:
1. Capability cards — each agent publishes a signed YAML card declaring tags, model, tool, and historical track record.
2. Contracts — every unit of work is a structured markdown contract with acceptance criteria and settlement notes.
3. Routing stats — a per-tag ε-greedy multi-armed bandit picks the citizen with the best confidence-weighted historical score, exploring 15% of the time to keep learning. Settled contracts ship lessons that update the stats on the next reconcile.

Two governance affordances on top:
- Chavruta (paired) review for high-stakes contracts (any contract with risk=high gets a second citizen as reviewer).
- Amendments — citizens propose changes to the constitution itself; ratified amendments are appended (never overwritten).

Vendor-agnostic, MIT-licensed, no daemon, no database — just a _polis/ folder plus two ~400-LOC Python scripts. Worked example with 3 citizens, a real leader-shift after a settled-contract lesson, and a ratified amendment is shipped at examples/research-team/.
```

### Install command
```
git clone https://github.com/yehudalevy-collab/polis-protocol ~/.claude/skills/polis-protocol
```

### Usage / Quickstart snippet
```
# After install, in any project root:
python3 ~/.claude/skills/polis-protocol/scripts/init_polis.py \
  --project-root . \
  --agent-id claude-citizen-1 \
  --vendor anthropic \
  --model claude-opus-4-7 \
  --project-name "My Project"

# Then route a contract with full audit trail:
python3 ~/.claude/skills/polis-protocol/scripts/route_contract.py \
  --polis-root _polis \
  --contract _polis/contracts/open/my-contract.md \
  --explain
```

### Tested with (which Claude products)
```
Claude Code (CLI), Claude.ai
```

### Tested with (other agent platforms)
```
OpenAI Codex CLI, Google Gemini CLI
```

### Plugin type
```
skill
```
(Alternative if asked: `workflow` or `coordination-protocol`. Avoid `mcp-server` — Polis is NOT an MCP server.)

### Documentation URL
```
https://github.com/yehudalevy-collab/polis-protocol#readme
```

### Demo video URL (optional — if form asks)
**If you have a 30–60s demo recorded:** paste its Loom/YouTube URL.

**If you don't:** leave blank or paste the worked example URL as the next-best demonstration:
```
https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team
```

**Quickest way to make a video if the form requires one:**
1. Install Kap from https://getkap.co (free, ~30 seconds)
2. Resize your Terminal window to ~800×500
3. Hit record, run these four commands (one per beat, ~5s each), stop:
   ```
   python3 scripts/init_polis.py --project-root . --agent-id claude-demo --vendor anthropic --model claude-opus-4-7 --project-name "Demo"
   ls _polis/
   python3 scripts/route_contract.py --polis-root _polis --contract _polis/contracts/open/literature-review.md --explain
   python3 scripts/route_contract.py --polis-root _polis --reconcile
   ```
4. Export as MP4 at 15 fps (Kap default). Upload to Loom or YouTube unlisted. Paste URL.

### Image / Banner (if requested)
```
https://raw.githubusercontent.com/yehudalevy-collab/polis-protocol/main/assets/banner.png
```

### Why this plugin is useful (free-text field, ≤300 words)
```
The fastest-growing gap in Claude Code workflows is multi-vendor coordination. As soon as a real codebase has more than one agent session running (Claude doing implementation, Codex doing review, Gemini handling translation), they have no shared state. Each session starts cold. Hardcoded AGENTS.md / CLAUDE.md / GEMINI.md files capture intent but never learn from outcomes.

Polis Protocol fills that gap with a markdown-only "polis" (Greek for "the body politic"):
- Capability cards version-control each agent's specialty, model, and historical track record
- Contracts are structured units of work that any citizen can pick up
- A multi-armed bandit routes contracts to the citizen with the best confidence-weighted score on the contract's tags, exploring 15% of the time to keep learning
- Settled contracts ship lessons that update the routing stats
- High-stakes contracts get chavruta (paired) review before settlement
- The protocol itself is amendable — citizens propose changes, votes are tallied, ratified amendments append to the constitution

For Anthropic specifically: Polis positions Claude as a peer in a multi-vendor team, not a silo. Worked examples in the repo show Claude as the primary research citizen, Codex as the frontend citizen, and Gemini as the Spanish-translation citizen — with one real recorded routing leader-shift after a chavruta lesson was filed about cultural mistranslation.

Vendor-agnostic by design — no daemon, no database, no cloud dependency. The whole protocol fits in a folder of markdown files plus two Python scripts (~400 LOC each). MIT licensed. CI green across Python 3.10–3.13. Already listed in 2 awesome-lists; 12 more PRs awaiting maintainer review.
```

### Screenshot / Asset URLs
Reference these in the form if it has image-upload fields (right-click → Copy image address from the rendered GitHub page):
```
https://raw.githubusercontent.com/yehudalevy-collab/polis-protocol/main/assets/banner.png
```

---

## Final checklist before submitting

- [ ] Repo is at `v0.1.0-alpha` or later (form may auto-detect; bumping to v0.2 first is a stronger signal)
- [ ] README has banner image visible (Task 2 of original launch plan)
- [ ] CI badge in README is green (https://github.com/yehudalevy-collab/polis-protocol/actions)
- [ ] All copy-paste fields above tested for non-ASCII characters (em-dashes can break some forms — replace with `--` if you see errors)
- [ ] Submit to BOTH https://clau.de/plugin-directory-submission AND https://platform.claude.com/plugins/submit — the forms are mirrors but reviewers may differ

## What happens after submission

1. **Within 24h:** Confirmation email (check spam — Anthropic's automated emails sometimes filter)
2. **Within 7 days:** Reviewer may comment requesting changes (security scan, license-clarification, category-recategorization)
3. **Within 14–21 days:** Either accepted into the directory or politely rejected with reason. Accepted entries appear in Claude Code's `/plugin marketplace` browser within ~48h of acceptance.
4. **If rejected:** Address the feedback and resubmit. There is no public ban-list for resubmissions provided the feedback is addressed.

## Tracking your submission

Save your form-submission confirmation email. The unique ID lets you reference your submission if you ever need to follow up via DM to Anthropic DevRel.
