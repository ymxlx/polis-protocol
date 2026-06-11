---
name: polis-protocol
description: Set up a self-optimizing multi-vendor AI agent team using the Polis Protocol — a markdown-based "small city" where each agent is a citizen with a content-hashed capability card, tasks are structured contracts routed to whoever has the strongest track record by a learning bandit, settled contracts produce lessons that compound into team memory, and citizens can ratify amendments to the protocol itself. Use whenever several AI agents (Anthropic, OpenAI, Google, or any vendor) collaborate on one project and "who should do this" is a real question; when you want work routed to whichever model is best at it; when you want a team that measurably gets better over time; or to set up a new polis, register or join as a citizen, open, claim, or settle a contract, file a lesson, propose or vote on an amendment, run a chavruta review before a high-stakes irreversible action, troubleshoot a stalled contract or router pathology, override a routing recommendation, or migrate from a simpler shared-vault setup (e.g. agent-vault) to add routing and self-improvement. Also trigger on "_polis folder", "polis", "capability card", "task contract", "chronicle.md", "chavruta review", "bandit routing", "agent routing", "cross-vendor coordination", "self-improving agent team", "register a citizen", "ratify an amendment", "CONSTITUTION.md", even when the user does not explicitly name the protocol. Pick this when optimization and team development matter, not only communication; for pure note-passing between agents without routing, prefer agent-vault.
---

# Polis Protocol: A Self-Optimizing City of Agents

A protocol that lets a team of AI agents from different vendors collaborate on a long-running project, route work to whoever is best at it, and get measurably better over time. The whole thing lives in a folder of markdown files, so any tool that can read and write text can participate.

## The core idea

Treat the project as a small *polis*: a city of citizens (the agents) that share a constitution (the protocol), publish public identities (capability cards), enter into contracts (tasks), and leave a public record of how things went (lessons). The polis has three institutions, and a fourth mechanism that lets the city itself change:

1. **The Register**: identity and capability discovery.
2. **The Contract**: structured tasks with learned routing.
3. **The Chronicle**: lessons that compound and feed back into routing.
4. **The Amendment**: a way for citizens to change the rules of the polis when reality demands it.

Together these give the team three things that simpler shared-vault approaches don't: cross-vendor optimization (work goes to whichever agent is actually best at it), self-development (the team's routing policy improves with use), and constitutional evolution (the protocol updates itself based on observed friction). Communication is the floor; this protocol aims at communication, optimization, and development at once.

The whole thing is portable because every artifact is a markdown file with structured YAML frontmatter. There is no central server. There is no required runtime. Any agent that can read and write text can participate.

## When this skill is active

Activate this skill when the user is doing any of the following:

- Setting up a new polis (bootstrapping the constitution, capability registry, contract folder, and chronicle).
- Joining an existing polis as a new agent (publishing a capability card, reading the constitution, catching up on the chronicle, claiming a contract).
- Writing a new contract (drafting intent and acceptance criteria, scoring candidate agents, routing).
- Settling a contract (recording the outcome, writing the lesson, updating capability stats).
- Running a chavruta review (paired critique of a high-stakes plan before execution).
- Proposing or ratifying an amendment to the protocol.
- Diagnosing a stalled contract, a sync conflict, a router pathology, or a quorum that cannot be reached.

If the user describes any multi-agent scenario where "who should do this" is a real question rather than "fine, whoever is available", this protocol applies. If the user already has agent-vault running and wants to upgrade, the migration path is straightforward (see `references/troubleshooting.md`, section "Migrating from agent-vault").

## Structure of a polis

A polis lives inside a folder called `_polis/` at the project root. The underscore prefix keeps it at the top of the file tree in Obsidian, VS Code, and most other tools. Everything outside `_polis/` is project content and the protocol does not touch it.

```
<project-root>/
├── CLAUDE.md / AGENTS.md / GEMINI.md        (cross-tool entry pointers)
├── .agents/skills/polis-protocol/SKILL.md   (Codex-format skill copy)
├── _polis/
│   ├── CONSTITUTION.md                      (canonical tool-agnostic protocol)
│   ├── README.md                            (protocol explainer for humans)
│   ├── index.md                             (canonical project state)
│   ├── chronicle.md                         (append-only event log)
│   ├── citizens/
│   │   └── <agent-id>/
│   │       ├── capability_card.yml          (content-hashed capability manifest)
│   │       ├── status.md                    (current state, last-seen pointer)
│   │       ├── inbox.md                     (messages from other citizens)
│   │       └── journal.md                   (private working notes)
│   ├── contracts/
│   │   ├── open/<contract-id>.md            (currently active)
│   │   ├── settled/<contract-id>.md         (closed with retrospective)
│   │   └── routing_stats.yml                (learned policy, updated on settle)
│   ├── lessons/
│   │   └── <capability-tag>/<lesson-id>.md  (filed by capability)
│   ├── reviews/
│   │   └── <YYYY-MM-DD-HHMM>-<contract>.md  (chavruta critique notes)
│   └── amendments/
│       ├── proposed/<amendment-id>.md
│       └── ratified/<amendment-id>.md
└── <project content folders>                (untouched)
```

Citizens link to project files using standard wikilinks (`[[path/to/note]]`). The `_polis/` folder is the only thing the protocol owns.

## The first thing to do every session

Before touching any project file, an agent runs the entry routine, in this order. This is the same shape as a well-run team meeting: read the state, hear what's pending for you, see what's in flight, then start work.

1. **Check that the polis exists.** Look for `_polis/CONSTITUTION.md` at the project root. If it does not exist, scaffold it (see "Founding a polis").
2. **Check that you are registered.** Look for `_polis/citizens/<self>/capability_card.yml`. If it does not exist, register (see "Registering a citizen").
3. **Read `_polis/CONSTITUTION.md` if you have not already in this session.** The constitution is the canonical version of this protocol; this SKILL.md is equivalent, but the constitution is what other tools read.
4. **Read `_polis/index.md`.** Short summary of where things stand. Two-minute read at most.
5. **Read your inbox.** `_polis/citizens/<self>/inbox.md` holds anything other citizens left for you.
6. **Scan the tail of `chronicle.md`.** Read backward from the end until you hit the timestamp recorded in your `status.md` under `last_seen_event:`. That is your catch-up.
7. **Read your open contracts.** Anything in `_polis/contracts/open/` with `owner: <self>` in its frontmatter.
8. **Update `last_seen_event` and `last_active` in your `status.md`.** This is how your next session knows where to pick up.
9. **Report back to the user.** A short summary: state of the project, what is in flight, what wants your input, and a concrete suggestion for the first move.

The whole routine should take a couple of small reads. If `chronicle.md` has grown large, the rollover policy (see `references/troubleshooting.md`) keeps it bounded.

## Recording what you did: the chronicle

After each meaningful action, append exactly one line to `_polis/chronicle.md`. The format is rigid on purpose, because the chronicle is parsed by the router and by other citizens, and an unreadable log is worse than no log at all.

```
- YYYY-MM-DD HH:MM | <agent-id> | <verb-phrase> | [[<wikilink>]] | <one-line note or - >
```

Examples:

```
- 2026-05-14 09:12 | claude-research-pesaj | drafted outline | [[contracts/open/literature-review]] | covers 2019-2025, 14 papers
- 2026-05-14 09:15 | codex-frontend-pesaj  | settled contract | [[contracts/settled/auth-refactor]] | tests passing, lesson filed
- 2026-05-14 09:18 | gemini-translator-es  | requested review | [[reviews/2026-05-14-0918-spanish-rollout]] | high-stakes, needs chavruta
```

A meaningful action is anything another citizen needs to know about: a contract opened or settled, a handoff, a blocker hit, a review requested, an amendment proposed, an index keeper change. Internal reasoning and minor edits stay in your private `journal.md` and never reach the chronicle. The signal-to-noise ratio of the chronicle is the single most important thing to protect.

Reserved verb phrases (these carry semantic meaning that scripts and other agents may filter on):

- `joined polis`, `left polis`: registration and retirement.
- `opened contract`, `claimed contract`, `settled contract`, `abandoned contract`: contract lifecycle.
- `filed lesson`: a retrospective was written into `lessons/`.
- `requested review`, `signed off`, `rejected review`: chavruta lifecycle.
- `proposed amendment`, `ratified amendment`, `rejected amendment`: amendment lifecycle.
- `blocked on <thing>`, `unblocked`: state transitions for tracking.
- `assumed index keeper`, `released index keeper`: rotation of the index-keeping role.

For everything else, use plain past-tense verbs.

## The Register: capability cards

Every citizen publishes one file: `_polis/citizens/<agent-id>/capability_card.yml`. This is the polis's answer to "who can do what". It replaces the unstructured profile of older protocols with something machine-parseable, so the router can actually use it.

A capability card looks like this:

```yaml
agent_id: claude-research-pesaj
vendor: anthropic
model: claude-opus-4-7
tool: claude.ai web
registered: 2026-05-14 09:00:00
languages: [es, en, he]
capability_tags:
  - long-context-reading: { self_rating: 5, evidence: "150k token context window" }
  - source-checking:      { self_rating: 4, evidence: "thorough but slow" }
  - spanish-translation:  { self_rating: 3, evidence: "native-ish but not certified" }
  - frontend-code:        { self_rating: 2, evidence: "can do simple HTML, not React" }
cost_envelope:
  relative: medium       # one of: low, medium, high
  notes: "API-priced, fine for non-trivial tasks"
latency_envelope:
  typical_minutes: 3
  max_minutes: 30
standing_instructions: |
  - Prefer simple, accessible vocabulary in written outputs.
  - When uncertain, ask before guessing.
content_hash: "sha256:abc123..."   # tamper-evidence, not a cryptographic signature
```

A few rules that keep this useful rather than ceremonial:

- **Self-ratings are starting points, not truth.** They seed the router. Actual performance (recorded in `routing_stats.yml`) takes over within a handful of tasks per tag.
- **Capability tags should be specific.** `frontend-code` is too vague; `react-component-design`, `css-responsive-layout`, and `tailwind-styling` are useful. Tags accrete naturally as contracts get written.
- **Edit your own card freely.** The card is a living document. When you learn you are bad at something, lower the rating. When you pick up a new tool, add the tag.
- **The `content_hash` is tamper-evidence, not security.** It is a SHA-256 of the card's content, so other citizens can tell if a card was edited since it was last stamped (`polis verify`). It does **not** prove *who* made the edit — real cryptographic identity is out of scope for a markdown protocol, which is why we don't call it a "signature".

When a new agent joins the polis, they write their own card. They do not need anyone's permission. The Register is open by design.

## The Contract: structured tasks with learned routing

Tasks in the polis are not free-form notes. They are contracts with three sections, written in that order over the lifetime of the contract:

1. **Intent** (written when the contract is opened): goal, acceptance criteria, required capability tags, deadline, cost ceiling, stakes level.
2. **Assignment** (written when a citizen claims or is routed to the contract): owner, planned approach, estimated effort.
3. **Settlement** (written when the contract closes): outcome, what worked, what bit the owner, lesson reference, quality score.

The full schema is in `references/protocol-spec.md`. Use the templates in `references/templates.md` when opening, claiming, or settling a contract.

### How contracts get routed

When a contract is opened, the router decides who to assign it to. The default routing policy is a multi-armed bandit:

- For each capability tag listed in the contract's `required_tags`, look up the historical performance of each registered citizen in `_polis/contracts/routing_stats.yml`.
- Score each citizen as a weighted combination of: self-rating (used heavily when there is no history yet), historical quality score on this tag, cost, and recent availability.
- Most of the time (the exploit setting), route to the top-scored citizen.
- Some of the time (the explore setting, defaults to 15%), route to a different citizen, to keep the policy honest about whether the leader is still actually the best.

The exact math, the cold-start handling, and how to tune the explore rate live in `references/routing.md`. The router can be a 60-line Python script (`scripts/route_contract.py`) or a brief reasoning step inside any agent's session. Both produce the same recommendation; the script just makes it cheap and consistent.

Routing is a recommendation, not a command. The user, or any citizen with reason to override, can claim a contract that the router did not recommend them for, by posting a one-line note in the contract's `Assignment` section explaining why. Overrides are also data: they get logged and contribute to the policy.

### Settling a contract and filing the lesson

When a contract closes, the owner does three things together:

1. Writes the `Settlement` section of the contract: outcome, quality self-score, what to do differently next time.
2. Creates a `lesson` file under `_polis/lessons/<capability-tag>/<lesson-id>.md`. One paragraph plus tags. This is what other citizens will read before taking similar contracts.
3. Posts a `settled contract` line in `chronicle.md`.

The router reads settled contracts and lessons periodically to update `routing_stats.yml`. That update is what makes the team get better over time.

## The Chronicle of lessons: how the team develops

The chronicle of events records what happened. The lessons folder records what was *learned*. The split matters because most events are not lessons, and most lessons distill many events.

A lesson is short and structured:

```yaml
---
lesson_id: 2026-05-14-spanish-rollout-1
filed_by: gemini-translator-es
capability_tags: [spanish-translation, cultural-vocabulary]
related_contracts: [contracts/settled/spanish-rollout]
quality_impact: 3   # 1=trivial, 5=changes how we route this tag
---
```

```
# Lesson: Spanish vocabulary in BA México context requires madrij not "líder"

When translating youth-movement content for the BA México audience, the
Hispanic-Spanish word "líder" reads as corporate; the loan-word "madrij"
(Hebrew for guide, used in the movement) is the right choice and is what
janijim expect. This applied across welcome packets, parent calls, and
event invites. Future Spanish-translation contracts for any BA México
property should default to madrij and similar movement vocabulary.
```

Lessons are *the* mechanism by which the polis improves. New contracts in the same capability tag pull recent lessons before being routed, so the routing decision and the executing agent both have the team's accumulated wisdom in context. Without this layer, every project is amnesiac; with it, the team builds institutional memory the way a real team does.

## Chavruta review for high-stakes contracts

Borrowed from the paired-study model of the beit midrash, *chavruta review* is the polis's safeguard against single-model failure. Any contract flagged `stakes: high` in its intent (deletes data, ships to production, makes an architectural call, commits the project to a direction that would be expensive to reverse) requires a second citizen from a *different vendor* to critique the plan before execution.

The flow:

1. Owner writes the `Assignment` section of the contract, including a "Plan" paragraph.
2. Owner posts `requested review` to the chronicle and writes a brief note in a reviewer's inbox. Pick a reviewer whose capability card shows strength in the relevant tag, ideally from a different vendor.
3. Reviewer reads the plan, writes a critique note under `_polis/reviews/<YYYY-MM-DD-HHMM>-<contract-id>.md`. The note answers three questions: "What is the owner getting right?", "What might they be missing?", "Sign off, request changes, or reject?"
4. If signed off, the owner executes. If changes are requested, the owner revises the plan and the cycle repeats once. If rejected, the owner either escalates to the user or abandons the contract.
5. The review note is linked from the contract's `Settlement` section when it closes.

Two citizens of the same vendor reviewing each other is allowed but weaker; the value of the chavruta is exactly the structural difference between models. The protocol does not enforce this, because a small polis may not have enough vendor diversity yet, but it strongly encourages it.

Low-stakes contracts skip review entirely. Most contracts are low-stakes. Use this mechanism sparingly so it stays meaningful.

## The Amendment: a polis that updates itself

Most protocols are frozen at design time. The Polis Protocol is not. When a citizen notices a recurring failure, an unclear rule, or a routing pathology, they can propose an amendment.

The flow:

1. Citizen writes `_polis/amendments/proposed/<amendment-id>.md`. The file states: the problem, the proposed change to the constitution, and any new file format or rule that follows.
2. Citizen posts `proposed amendment` to the chronicle and a one-line pointer to every citizen's inbox.
3. Other citizens read and respond. Responses are appended to the amendment file as `### <YYYY-MM-DD> from <agent-id>: agree | disagree | abstain | request changes`, with a short rationale.
4. When a quorum is reached (default: simple majority of currently active citizens, where "active" means a chronicle entry in the last 14 days), the proposing citizen, or any citizen, can move the file to `_polis/amendments/ratified/` and edit `_polis/CONSTITUTION.md` to reflect the change. Both actions get one chronicle line each.
5. Rejected amendments stay in `proposed/` with `status: rejected` in their frontmatter. They are not deleted; future citizens may want to know what was tried.

Amendments are how the protocol becomes the team's protocol. The default rules in this skill are a starting point; over time, a given polis will diverge in small ways that fit the project it serves. That divergence is a feature, not a bug. The constitution is always the canonical version for any specific polis; this SKILL.md is the seed it grew from.

## Founding a polis

When the user wants to start a new polis (or when an agent enters a project that does not yet have one), bootstrap it.

The fastest path is the published CLI — `uvx` always fetches the latest release from PyPI, so users stay current automatically:

```
uvx polis-protocol init \
  --project-root <path> \
  --agent-id <your-agent-id> \
  --vendor <anthropic|openai|google|other> \
  --model <model-id> \
  --project-name "<name>"
```

(Equivalent: `pipx install polis-protocol` then `polis init …`; or, from a repo checkout, `python scripts/init_polis.py …` with the same flags.)

The command writes the full `_polis/` structure, the constitution, a first capability card for the founding agent, a seed `chronicle.md`, an empty `routing_stats.yml`, and the cross-tool bridge pointers (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) at the project root. It is idempotent and never overwrites existing files; `polis init --repair` restores any missing managed files, and `polis migrate --plan|--apply|--rollback` handles schema upgrades reversibly.

If running the script is not available (the user is in a sandbox without Python, for example), bootstrap by hand using the templates in `references/templates.md`. The minimum viable polis is just `_polis/CONSTITUTION.md` plus your own capability card plus an empty `chronicle.md` with a frontmatter block.

## Registering a citizen into an existing polis

When you (an agent) arrive at a project that already has `_polis/CONSTITUTION.md` but no card for you under `_polis/citizens/<your-id>/`, register yourself. Do not wait for permission.

1. Pick an agent ID following the naming rule below.
2. Create your folder under `_polis/citizens/<your-id>/`.
3. Write your `capability_card.yml` (see schema in `references/protocol-spec.md`).
4. Create empty `status.md`, `inbox.md`, and `journal.md` from the templates.
5. Post a `joined polis` line in `chronicle.md` with your card as the wikilink.
6. Continue with the entry routine.

### Agent ID convention

Use the format `<vendor-or-tool>-<role>-<project>`. The vendor-or-tool prefix matters because it lets any citizen scanning the chronicle see at a glance which model produced which line, which helps both with debugging (some vendors have characteristic failure modes) and with cross-vendor routing.

Good examples: `claude-research-pesaj`, `codex-frontend-pesaj`, `gemini-translator-pesaj`, `gpt-copywriter-pesaj`.

Bad examples: `agent-7a3f` (opaque), `helper` (too generic), `gemini-2026-05-14-1430` (timestamps are not identity).

Lowercase, hyphens only, 8 to 40 characters. Once registered, do not rename; old chronicle lines will still reference the original ID.

## Granularity guidance

The most common failure mode is over-recording. Calibration table:

| Action | Chronicle? | Lesson? | Capability card edit? |
|---|---|---|---|
| Fixed a typo in a contract | No | No | No |
| Drafted a substantial new section | Yes | No | No |
| Settled a contract | Yes | Yes | Maybe |
| Discovered you are bad at a thing | No | Yes | Yes (lower rating) |
| Discovered you are great at a thing | No | Yes | Yes (raise rating) |
| Hit a real blocker | Yes (with `blocked on`) | Maybe | No |
| Made an architectural decision | Yes | Yes | No |
| Saw the same kind of issue three times in a row | No | One lesson summarizing | Maybe |
| Noticed the protocol itself is the problem | No, propose an amendment | No | No |

When in doubt: would another citizen waste time, make the wrong call, or duplicate work if this is not recorded? If yes, record it. If no, do not.

## Working across vendors

The protocol is vendor-agnostic. The same polis can be shared between Claude, Codex, Gemini CLI, GPT-based tools, and anything else that reads markdown. The bootstrap writes four extra files for cross-tool discovery:

- `<project-root>/CLAUDE.md`: entry pointer for Claude Code.
- `<project-root>/AGENTS.md`: entry pointer for Codex (and Jules, Aider, goose, opencode, Zed, Warp, VS Code, Devin).
- `<project-root>/GEMINI.md`: entry pointer for Gemini CLI.
- `<project-root>/.agents/skills/polis-protocol/SKILL.md`: a Codex-format skill copy.

All four point to `_polis/CONSTITUTION.md`. Updating the protocol means editing that one file; pointers stay stable.

Cross-vendor routing is where this protocol earns its keep: the bandit will route a Spanish translation to whichever citizen has the best track record on `spanish-translation`, not whichever one happens to be the user's current chat. Over time, this means the team's outputs are not bottlenecked by any single model's blind spots.

## Failure modes and recovery

A short list. The extended version is in `references/troubleshooting.md`.

- **A citizen has gone silent.** Check their `status.md` and last chronicle entry. If a contract is stuck, post to their inbox. If they have been inactive past the project's stale threshold (default 14 days), file a one-amendment-line transfer of ownership and proceed.
- **Two citizens claimed the same contract.** First-write-wins on the contract's `owner:` field. The losing citizen posts a chronicle line, drops the claim, and either picks another contract or posts to the winner's inbox offering help.
- **The router keeps picking the wrong citizen.** Check `routing_stats.yml`; it may be cold-start (not enough data). Override manually for a few contracts to seed the policy. If it persists, propose an amendment to the routing weights.
- **A capability card was edited by someone other than the owner.** The `content_hash` mismatch (`polis verify`) will flag it. Treat as a sync conflict, restore from history, and post a chronicle line.
- **An amendment is stuck without a quorum.** Lower the activity threshold temporarily, or merge the amendment with related proposals to attract more responses. Amendments that sit for 30 days auto-expire.
- **The polis is growing too large.** Roll over `chronicle.md` quarterly (`chronicle-YYYY-Qn.md`) and archive settled contracts older than 90 days. Lessons never roll over; they are the team's memory.

## References

For deeper detail, consult these files. Each is short and focused.

- `references/protocol-spec.md`: full schema for every file (capability card, contract, lesson, amendment, review note, status, inbox). Read this when you need to validate a file or parse another citizen's output.
- `references/templates.md`: copy-paste templates for every file the protocol uses, with inline annotations. Read this when opening a contract, registering, filing a lesson, or proposing an amendment.
- `references/routing.md`: the bandit math, scoring formulas, cold-start handling, explore-rate tuning, and how the router updates `routing_stats.yml` on settlement. Read this when you need to understand or override a routing decision.
- `references/amendments.md`: deeper guidance on when an amendment is the right move versus a one-off workaround, the quorum rules, and worked examples of past amendments.
- `references/troubleshooting.md`: failure modes, recovery procedures, scaling guidance, and the migration path from agent-vault.
- `templates/POLIS_CONSTITUTION.md`: the tool-agnostic canonical protocol that gets written into each polis on bootstrap. The source of truth when refreshing a polis's constitution.

Read the spec when validating a file format. Read the templates when bootstrapping or claiming. Read routing when the bandit picks weird. Read amendments when reaching for a rule change. Read troubleshooting when something broke.
