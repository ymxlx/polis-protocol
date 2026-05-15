<p align="center">
  <img src="assets/banner.png" alt="Polis Protocol — three AI agents, one protocol, unified intelligence" width="100%" />
</p>

# Polis Protocol

> A self-optimizing city of AI agents. A team of Claude, Codex, Gemini, and any other vendor can share one project, route work to whoever is best at it, and measurably get better over time — using nothing but a folder of markdown files.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/format-Claude%20Skill-blueviolet)](https://github.com/yehudalevy-collab/polis-protocol)
[![Vendor-agnostic](https://img.shields.io/badge/vendor-agnostic-success)]()

---

## What it is

Most multi-agent coordination tools stop at *communication* — a shared scratchpad where agents can leave notes for each other. That is the floor. The Polis Protocol aims higher:

1. **Communication** — every meaningful action lands in an append-only `chronicle.md`.
2. **Optimization** — tasks are structured contracts, routed to whichever citizen has the strongest track record on the required capability tags by a multi-armed-bandit policy.
3. **Self-development** — every settled contract produces a structured lesson; lessons feed back into the router so the team's wisdom compounds.
4. **Constitutional evolution** — when a rule stops working, citizens can propose, vote on, and ratify amendments to the protocol itself.

The whole thing lives in a folder. There is no central server, no required runtime, no proprietary format. If a tool can read and write markdown, it can participate.

---

## Why "polis"

A *polis* is a small Greek city — a few thousand people who all know each other and run their own affairs. The metaphor maps cleanly:

| Polis | Polis Protocol |
|---|---|
| Citizen | An AI agent from any vendor |
| Capability card | A signed YAML manifest of what an agent can do |
| Contract | A structured task with intent, assignment, and settlement |
| Chronicle | An append-only event log every citizen reads on session start |
| Lesson | A retrospective filed by capability tag |
| Chavruta | A paired critique by a citizen from a different vendor before a high-stakes action |
| Amendment | A vote-ratified change to the constitution |

It is opinionated on purpose. The names are sticky, the file format is rigid, the chronicle line shape is non-negotiable. Rigidity at the protocol layer is what lets four different vendors' models read the same folder and agree on what they're looking at.

---

## Quick start

### 1. Install the skill (Claude Code)

Drop `polis-protocol.skill` into your Claude Code skills folder, or just clone this repo:

```bash
git clone https://github.com/yehudalevy-collab/polis-protocol.git
```

### 2. Found a polis

```bash
python polis-protocol/scripts/init_polis.py \
  --project-root /path/to/your/project \
  --agent-id claude-research-yourproject \
  --vendor anthropic \
  --model claude-opus-4-7 \
  --tool "claude code" \
  --project-name "Your Project Name"
```

You now have:

```
your-project/
├── CLAUDE.md / AGENTS.md / GEMINI.md     ← cross-tool entry pointers
├── .agents/skills/polis-protocol/SKILL.md ← Codex-format mirror
└── _polis/
    ├── CONSTITUTION.md                    ← canonical protocol
    ├── README.md
    ├── index.md                           ← "where things stand"
    ├── chronicle.md                       ← append-only event log
    ├── citizens/<you>/                    ← capability_card, status, inbox, journal
    └── contracts/
        ├── open/                          ← active tasks
        ├── settled/                       ← closed tasks with lessons
        └── routing_stats.yml              ← learned routing policy
```

### 3. Open a contract

Drop a file in `_polis/contracts/open/`:

```yaml
---
contract_id: literature-review
opened_by: claude-research-yourproject
status: proposed
stakes: medium
required_tags: [long-context-reading, source-checking]
cost_ceiling: medium
---

# Literature review of multi-agent coordination protocols
...
```

### 4. Route it

```bash
python polis-protocol/scripts/route_contract.py \
  --polis-root _polis \
  --contract _polis/contracts/open/literature-review.md \
  --explain
```

Output:

```
Score breakdown:
  claude-research-yourproject  total=0.430  hist=0.00  self=0.90  cost=1.00  avail=1.00
  codex-frontend-yourproject   total=0.350  hist=0.00  self=0.50  cost=1.00  avail=1.00

Recommendation: claude-research-yourproject
```

### 5. Settle and learn

When the contract closes, the owner files a lesson under `_polis/lessons/<tag>/`. Then:

```bash
python polis-protocol/scripts/route_contract.py --polis-root _polis --reconcile
```

The bandit's `routing_stats.yml` updates. Next time a similar contract opens, the routing decision is sharper.

---

## The four institutions

### The Register

Every citizen publishes one file: `_polis/citizens/<agent-id>/capability_card.yml`. Vendor, model, languages, capability tags with self-ratings, cost envelope, latency envelope, standing instructions, signature. The card is the polis's answer to "who can do what". No central directory, no permission needed to join — the Register is open by design.

### The Contract

Tasks are three-section markdown files:

- **Intent** — goal, acceptance criteria, required tags, deadline, cost ceiling, stakes
- **Assignment** — owner, plan, estimated effort (filled when claimed)
- **Settlement** — outcome, quality self-score, what worked, what bit (filled when closed)

Open contracts live in `contracts/open/`. Settled contracts move to `contracts/settled/` and never get deleted. The shape of a contract is fixed so any citizen — and the router — can read every contract without guessing the schema.

### The Chronicle

`_polis/chronicle.md` is an append-only event log. One line per meaningful action:

```
- 2026-05-14 09:12 | claude-research-pesaj | drafted outline | [[contracts/open/literature-review]] | covers 2019-2025, 14 papers
- 2026-05-14 09:15 | codex-frontend-pesaj  | settled contract | [[contracts/settled/auth-refactor]] | tests passing, lesson filed
- 2026-05-14 09:18 | gemini-translator-es  | requested review | [[reviews/2026-05-14-0918-spanish-rollout]] | high-stakes, needs chavruta
```

Reserved verbs (`opened contract`, `claimed contract`, `settled contract`, `filed lesson`, `requested review`, `proposed amendment`, `blocked on <thing>`, …) carry semantic weight that the router and other citizens parse on.

Lessons live separately in `_polis/lessons/<capability-tag>/`. The chronicle records what happened; the lessons record what was *learned*. Most events are not lessons, and most lessons distill many events.

### The Amendment

When a rule stops working, any citizen can propose a change. The proposal goes in `_polis/amendments/proposed/<id>.md`. Other citizens append response blocks: `agree | disagree | abstain | request_changes`. When a simple majority of active citizens (those with a chronicle line in the last 14 days) agree, the file moves to `amendments/ratified/` and the constitution is edited.

The protocol changes itself. The default rules in this skill are the seed; over time a given polis will diverge in small ways that fit its project. That divergence is the point.

---

## Chavruta review

Borrowed from the paired-study model of the beit midrash, *chavruta review* is the polis's safeguard against single-model failure. Any contract flagged `stakes: high` requires a second citizen from a different vendor to critique the plan before execution. The critique answers three questions:

> What is the owner getting right? What might they be missing? Decision: signed_off, requested_changes, or rejected.

Two citizens of the same vendor reviewing each other is allowed but weaker — the value of the chavruta is exactly the structural difference between models. Use it sparingly. Most contracts are low-stakes.

---

## How the router learns

The default router is a multi-armed bandit:

- **Exploit** (85%): route to the citizen with the highest combined score on the required tags. The score weights historical quality (55%), self-rating (20%), cost fit (15%), and current availability (10%).
- **Explore** (15%): route to a non-top citizen, weighted by score, to keep the policy honest about whether the current leader is still actually best.
- **Cold start**: when no history exists for a tag, self-ratings dominate. Self-ratings get displaced within a handful of contracts per tag.

When a contract settles, `routing_stats.yml` updates with the new quality score and minutes. That update is what makes the team get better over time. The full math is in [`references/routing.md`](references/routing.md).

You can run the router as:

- a 60-line Python script (`scripts/route_contract.py`),
- a brief reasoning step inside any agent's session (the math is small enough to do in-context).

Both produce the same recommendation. Citizens can always override.

---

## Repository contents

| Path | What it is |
|---|---|
| [`SKILL.md`](SKILL.md) | The Claude Code skill: when to activate, full workflow |
| [`scripts/init_polis.py`](scripts/init_polis.py) | Bootstrap a new polis (idempotent, signed cards, bridge pointers) |
| [`scripts/route_contract.py`](scripts/route_contract.py) | The bandit router and the `--reconcile` job that rebuilds stats from settled contracts |
| [`templates/POLIS_CONSTITUTION.md`](templates/POLIS_CONSTITUTION.md) | The canonical constitution written into every new polis |
| [`templates/bridge_pointer.md`](templates/bridge_pointer.md) | The short `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` that points each tool at the constitution |
| [`references/protocol-spec.md`](references/protocol-spec.md) | Full schema for every file (cards, contracts, lessons, amendments, reviews, status, inbox) |
| [`references/templates.md`](references/templates.md) | Copy-paste templates for every file the protocol uses |
| [`references/routing.md`](references/routing.md) | Bandit math, cold-start, explore-rate tuning, stats update procedure |
| [`references/amendments.md`](references/amendments.md) | When to amend vs. when to file a lesson; quorum rules; worked examples |
| [`references/troubleshooting.md`](references/troubleshooting.md) | Failure modes, recovery, scaling, and the migration path from `agent-vault` |

---

## Working across vendors

The protocol is vendor-agnostic. The same polis can be shared by Claude, Codex, Gemini CLI, GPT-based tools, and anything else that reads markdown. Bootstrap writes four discovery pointers:

- `CLAUDE.md` — entry point for Claude Code
- `AGENTS.md` — entry point for Codex (and Jules, Aider, goose, opencode, Zed, Warp, VS Code, Devin)
- `GEMINI.md` — entry point for Gemini CLI
- `.agents/skills/polis-protocol/SKILL.md` — a Codex-format skill mirror

All four point at one place: `_polis/CONSTITUTION.md`. Updating the protocol means editing that one file.

Cross-vendor routing is where this protocol earns its keep. A Spanish translation goes to whichever citizen has the best track record on `spanish-translation`, not whichever happens to be the user's current chat. Over time, that means team output stops being bottlenecked by any single model's blind spots.

---

## Relationship to `agent-vault`

[`agent-vault`](https://github.com/yehudalevy-collab/agent-vault) is a sister project: a simpler, communication-only protocol where agents share an Obsidian-style markdown blackboard. If you only need agents to leave each other notes, `agent-vault` is enough.

Pick **Polis Protocol** when:

- You have agents from multiple vendors and routing matters.
- You want the team to measurably get better over time.
- You want a way to amend the protocol itself when reality demands it.

The migration path from `agent-vault` is documented in [`references/troubleshooting.md`](references/troubleshooting.md).

---

## Status

Reference implementation. The protocol is intentionally minimal — every file is markdown, every script is plain Python stdlib (`route_contract.py` adds one optional `PyYAML` dependency for parsing capability cards). Forks, issues, and amendments welcome.

---

## License

[MIT](LICENSE) — Yehuda Levy, 2026.
