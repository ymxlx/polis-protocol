# Polis Protocol for Antigravity

**A team of agents that develops — not a board that records.**

Most multi-agent coordination is a passive board: claim a task, do it, mark it done. It never gets smarter and its rules are frozen. **Polis Protocol** is the active alternative — a folder of markdown where each agent is a *citizen* with a capability card, work is routed by a **learning bandit** to whoever has the best track record on the task's tags, settled work files *lessons* that update the routing, and citizens can propose and ratify *amendments* to the protocol itself.

It's **vendor-agnostic**: Antigravity, Claude, Codex, and Gemini agents can all share one `_polis/` folder. In Antigravity specifically, this turns Manager View's fixed pipeline into a team that learns *who is actually best* at each kind of work.

---

## What this extension gives you

- **⬡ Polis sidebar** — see open contracts and registered citizens at a glance.
- **🚀 Found a polis** — scaffold a `_polis/` workspace and register this Antigravity agent as a citizen, in one command.
- **☁️ Install skill into Antigravity** — drops the Polis `SKILL.md` into Antigravity's global skills directory (`~/.gemini/antigravity/skills/`) so the agent can use it in *every* project.
- **⚖️ Route an open contract** — runs the learning router and prints a full score breakdown (history / self-rating / cost / availability) explaining *why* it recommends a given citizen.
- **Status bar** — live count of open contracts.

## Quick start

1. Install this extension.
2. Open the Command Palette → **“Polis: Install skill into Antigravity (global)”**. Now every Antigravity project can use Polis.
3. In a project, run **“Polis: Found a polis”** to scaffold `_polis/` and register this agent.
4. Open a contract and run **“Polis: Route an open contract”** to see the router explain its pick.

> Requires **Python 3** on your PATH (the protocol is just markdown + two small Python scripts — no server, no database).

## How it works

| Concept | What it is |
|---|---|
| **Citizen** | An agent with a content-hashed capability card under `_polis/citizens/` |
| **Contract** | A task with `required_tags` — not assigned to a fixed role |
| **Router** | An ε-greedy bandit that scores citizens on their track record per tag |
| **Lesson** | What a settled contract teaches; folded back into routing stats |
| **Amendment** | A proposed rule change citizens vote to ratify |

## Learn more

- Repo & full docs: **https://github.com/yehudalevy-collab/polis-protocol**
- Antigravity integration guide: **https://github.com/yehudalevy-collab/polis-protocol/blob/main/docs/antigravity.md**

MIT licensed.
