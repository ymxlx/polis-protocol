# Polis Protocol + Google Antigravity

Google Antigravity is an agent-first IDE: a "Manager View" decomposes a task and
runs specialized subagents in parallel. The default orchestration is a **fixed
pipeline** — the same roles run in the same order every time, with no notion of
which agent has actually been best at a given kind of work, and no way for the
team to change its own rules.

Polis Protocol is the layer that makes that orchestration **learn**. Drop a
`_polis/` into an Antigravity project and the team gains a track record, a
learning router, and a constitution its agents can amend — without leaving
markdown.

---

## Why this pairing works

| | Antigravity Manager View (alone) | With Polis Protocol |
|---|---|---|
| Who does a task | Fixed role in a hardcoded pipeline | Routed to whoever has the best track record on the task's tags |
| Does it improve | No — same pipeline every run | Yes — settled tasks file lessons that update routing |
| Cross-vendor | Gemini-centric | Any agent that reads markdown (Claude, Codex, Gemini, …) |
| Can the rules change | No | Yes — citizens propose and vote on amendments |

Antigravity supplies the **runtime** (parallel agents, sandboxes, the IDE).
Polis supplies the **coordination memory** (who's good at what, what we learned,
what the rules are). They compose cleanly.

---

## Setup (60 seconds)

From your Antigravity project root:

```bash
curl -fsSL https://raw.githubusercontent.com/yehudalevy-collab/polis-protocol/main/install.sh | bash -s -- \
  --agent-id gemini-antigravity-yourproject \
  --vendor google \
  --model gemini-3 \
  --tool "antigravity"
```

This writes everything Antigravity reads on startup:

- **`.antigravity/skills/polis-protocol/SKILL.md`** — Antigravity loads skills
  from `.antigravity/skills/` automatically. This is the canonical skill entry.
- **`GEMINI.md`** and **`AGENTS.md`** — Antigravity reads both for instructions;
  each points at `_polis/CONSTITUTION.md`.
- **`.agents/skills/polis-protocol/SKILL.md`** — Codex-format mirror, so the same
  project also works in Codex/Cursor/others without changes.
- **`_polis/`** — the canonical protocol state (citizens, contracts, chronicle,
  routing stats, lessons, amendments).

Nothing is Antigravity-specific in the protocol itself — that's the point. The
same `_polis/` works whether the agent picking it up is in Antigravity, Claude
Code, or Codex.

---

## Using Polis from inside Manager View

Instead of letting Manager View route by fixed role, have the manager consult the
router before delegating. The pattern:

1. **Register each subagent as a citizen.** When Manager View spins up a
   frontend agent and a testing agent, each writes a capability card under
   `_polis/citizens/`. (The skill instructs the agent to do this on first run.)

2. **Open a contract instead of assigning a role.** Rather than "frontend agent,
   build the form," open a contract with `required_tags: [react, forms]`. Then:

   ```bash
   python3 _polis/../scripts/route_contract.py \
     --polis-root _polis \
     --contract _polis/contracts/open/build-signup-form.md \
     --explain
   ```

   The router recommends the citizen with the best history on those tags — which
   after a few sprints may not be the agent labeled "frontend."

3. **Settle and file a lesson.** When the subagent finishes, it records the
   outcome and a one-line lesson. `--reconcile` folds it into the routing stats,
   so next sprint's routing is sharper.

4. **Amend when a rule stops working.** If Manager View's defaults conflict with
   what the team has learned (e.g. a quality threshold is too low), a citizen
   proposes an amendment and the others vote. Ratified amendments live in
   `_polis/amendments/ratified/`.

The result: Antigravity's parallelism, plus a team that develops instead of
re-running the same pipeline forever.

---

## What Antigravity reads, and where Polis writes it

| Antigravity expects | Polis writes | Purpose |
|---|---|---|
| `.antigravity/skills/<name>/SKILL.md` | ✅ on `init` | The Polis skill, auto-loaded |
| `GEMINI.md` | ✅ on `init` | Points Antigravity at the constitution |
| `AGENTS.md` | ✅ on `init` | Cross-tool instruction pointer |
| `_polis/CONSTITUTION.md` | ✅ on `init` | The canonical, amendable rulebook |

If you only want the Antigravity surface and not the others, pass
`--bridge-tools gemini --no-codex-skill` (the `.antigravity/skills/` copy is on by
default; suppress it with `--no-antigravity-skill`).

---

## FAQ

**Does Polis replace Manager View?** No. Manager View runs the agents; Polis
decides who should get the work and remembers how it went. Use both.

**Is this Gemini-only?** No. Antigravity is Gemini-centric, but a Polis project
is vendor-agnostic — a Claude Code or Codex session can open the same `_polis/`
and participate as a citizen.

**Do I need the Python scripts?** The router is a ~60-line script, but the math
is small enough that an agent can run the routing decision as a reasoning step in
context. The scripts are the reproducible path; in-context routing is the
zero-dependency path.
