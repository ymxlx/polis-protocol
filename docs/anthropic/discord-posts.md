# Anthropic-related Discord posts

Each section is the exact copy to paste into the relevant channel. Don't mass-paste — write your custom lead sentence per server using their recent topics.

**Critical rule:** Read the last 20 messages in the channel BEFORE posting. If someone just asked about multi-agent coordination, lead with "Saw the multi-agent thread above — built this for exactly that."

---

## 1. Anthropic Builders Discord — `#show-and-tell` or `#projects`

**Server invite (if not joined):** Check https://www.anthropic.com/builders or https://discord.com/invite/anthropic

**Post:**

```
Just shipped Polis Protocol — a markdown coordination layer for multi-vendor agent teams that lets Claude Code, Codex, and Gemini work as one team on the same project.

Three primitives:
- Signed capability cards (YAML) — every agent publishes what they're good at + historical track record
- Bandit-routed contracts — work goes to the citizen with the best confidence-weighted score on the contract's tags
- Chavruta paired review — high-stakes contracts get a second citizen as reviewer before settlement

Plus an amendment process so the protocol itself can evolve. The repo ships a worked example with three real citizens, a recorded routing leader-shift after a lesson, and a ratified amendment.

Vendor-agnostic — works with anything that reads markdown. No daemon, no database.

Repo: https://github.com/yehudalevy-collab/polis-protocol
Worked example: https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team

Curious for feedback from anyone running multi-vendor agent setups today — what coordination pain points are you hitting that this doesn't address?
```

**Why this works:** Asks a specific question at the end. Discord posts that end in a question get 4x more replies than declarative posts.

---

## 2. Claude Code Community Discord — `#share-your-creations` or equivalent

```
Built a multi-vendor agent coordination layer that works as a Claude Code skill — Polis Protocol.

If you're running Claude Code alongside Codex or Gemini CLI on the same project (or thinking about it), this gives them a shared "polis" they can all read and write to. Each agent has a capability card; work is routed by a bandit that learns from settled-contract outcomes; high-stakes contracts get paired review before settlement.

The interesting bit is the amendment process — citizens can propose changes to the protocol itself, and ratified amendments append to a constitution. The worked example shows one real amendment changing the routing rules.

Drop it into ~/.claude/skills/polis-protocol and you're done — it ships AGENTS.md and GEMINI.md bridge files automatically so the polis works across tools.

Repo: https://github.com/yehudalevy-collab/polis-protocol

Anyone here running multi-vendor agents on shared codebases? Would love to know which contract-types break first in your setup.
```

---

## 3. AI Engineer Foundation Discord — `#projects`

```
Open-sourced a vendor-agnostic agent coordination protocol — Polis Protocol.

The thesis: declarative configs (AGENTS.md, CLAUDE.md) capture intent but never learn from outcomes. So I built a markdown polis where each agent publishes a capability card, contracts are routed by an ε-greedy multi-armed bandit, and settled contracts ship lessons that update the routing stats.

Two governance affordances on top: chavruta paired review for high-stakes contracts, and a ratifiable amendment process so the protocol itself evolves.

Worked example with 3 citizens (Claude / Codex / Gemini), a recorded leader-shift after a routing-pollution lesson, and a ratified amendment: https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team

MIT, no daemon, no database. Looking specifically for feedback on whether the bandit's 15% exploration rate makes sense for low-volume contract streams (default), or if it should auto-scale based on contract throughput.
```

**Why this works for AI Engineer Foundation:** Pitches the technical detail (bandit math) that this community rewards.

---

## 4. LangChain Discord — `#projects` or `#langgraph`

```
Built a coordination layer that sits *underneath* LangGraph (or any agent runtime) — Polis Protocol.

The pitch: LangGraph is great for orchestrating *within* a vendor; Polis handles coordination *across* vendors when your team uses Claude + Codex + Gemini on the same project. Each agent gets a signed capability card; work is bandit-routed by historical performance; settled contracts produce lessons that update routing on the next reconcile.

Specifically curious how LangGraph users would feel about wrapping a Polis polis inside a LangGraph workflow — the affordances might compose well (LangGraph for the in-vendor state machine, Polis for the cross-vendor routing decision).

Repo: https://github.com/yehudalevy-collab/polis-protocol
```

---

## 5. LlamaIndex Discord — `#projects` or `#showcase`

```
Multi-vendor agent coordination protocol — Polis Protocol — open-sourced today.

Works alongside LlamaIndex agents as a routing + learning layer. The structure: each agent publishes a YAML capability card, contracts are markdown files in a versioned `_polis/` folder, and a multi-armed bandit picks the right citizen per contract. Settled contracts ship lessons that update the routing stats.

If you've got a LlamaIndex pipeline that uses multiple LLM providers (Claude for reasoning, GPT for tool-calling, Gemini for translation, etc.), Polis is the coordination layer that wraps them.

Worked example in the repo: https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team

Feedback welcome.
```

---

## 6. CrewAI Discord — `#show-and-tell` (be careful here — CrewAI is *adjacent*, frame Polis as complementary not competitive)

```
Open-sourced a markdown coordination protocol that's vendor-agnostic — Polis Protocol.

CrewAI is great for orchestrating a *crew* of agents from one vendor. Polis is the layer one level above: when your CrewAI crew needs to coordinate with a Codex session OR a Gemini CLI session that's *also* working on the same repo, the polis is the shared state.

Three primitives: capability cards, bandit-routed contracts, ratifiable amendments. Worked example with a 3-citizen team and a real routing leader-shift after a settled-contract lesson.

Repo: https://github.com/yehudalevy-collab/polis-protocol

Would love to know if anyone here has hit the "CrewAI works great until I want to add a non-CrewAI agent" wall — that's exactly the gap Polis is designed for.
```

**Why this works for CrewAI:** Names CrewAI's strength (within-vendor crew) and identifies a specific gap (cross-vendor) without dunking on CrewAI. Maintainer-safe.

---

## 7. Cursor Discord — `#show-and-tell`

```
Polis Protocol — markdown coordination layer for when you're using Cursor + Claude Code (or any other agent) on the same project.

The pitch: Cursor's strength is in-editor speed; Claude Code's strength is depth + planning. They never talk to each other. Polis gives them a shared `_polis/` folder of markdown files — capability cards say who's good at what, contracts route work, settled contracts ship lessons that update routing.

If you've ever had a Cursor session and a Claude Code session step on each other's work, this is the coordination layer. MIT, no daemon, drop it in `~/.claude/skills/polis-protocol`.

Repo: https://github.com/yehudalevy-collab/polis-protocol
```

---

## Posting cadence

- **Don't post in more than 2 servers in the same day.** Aggressive cross-posting triggers spam filters and mod attention.
- **Space posts 24h apart.** Two per day max.
- **Reply to every comment within 2 hours during business hours.** This is the highest-leverage time investment in this list.
- **Pin the message in your X profile after posting** to one of these servers so people who click through have a clear next step.

## What you're hoping for

A reply that starts with one of these phrases:
- "Have you seen X?" (introduces you to an adjacent project)
- "I tried this and it..." (real user feedback — gold)
- "How does this compare to Y?" (frame-confirming engagement)
- "Mind if I share this with [team / colleague / community]?" (amplification request)

Any of those four = post worked. Plain likes = post landed but didn't activate.
