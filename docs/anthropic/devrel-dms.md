# DM templates for Anthropic DevRel + adjacent voices

**Rule #1:** Send these from your *personal* Twitter/X account, not a project account. People reply to humans, not project mouthpieces.

**Rule #2:** Send 1 per day at most. The DMs below are ranked — start with #1 and only send #2 if #1 doesn't reply in 5 days.

**Rule #3:** Attach the banner image OR a 30s demo clip if you have one. Visual attachments lift DM reply rates ~3x. If neither is available yet, the message is still worth sending without media.

---

## Tier 1 — Anthropic-employed DevRel (highest priority)

### 1.1 Alex Albert (@alexalbert__)

**Why:** Head of Claude DevRel. Looks at every credible Claude-adjacent skill submission. Replies to ~10% of well-targeted DMs.

**Message:**
```
Hi Alex — built a vendor-neutral coordination protocol for multi-agent teams. Lets Claude Code, Codex, and Gemini work on the same project with a shared "polis" — capability cards + bandit-routed contracts + an amendment process so the protocol itself evolves.

Submitted to clau.de/plugin-directory-submission too, but figured I'd share directly in case it's interesting. Worked example with 3 citizens (Claude as primary), a recorded leader-shift after a chavruta-review lesson:

https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team

Specifically curious if the "AI agents review each other before settlement" pattern aligns with where Claude's safety story is heading. Happy to send a 30s demo or hop on a quick call if you'd find it useful.
```

**Why this works:** Acknowledges the formal channel was already used, offers a specific safety-narrative hook, ends with a low-friction call-to-action.

---

### 1.2 Maggie Appleton (@Mappletons)

**Why:** Designer-engineer at Anthropic, deeply interested in protocols and "knowledge work for agents." High signal-to-noise reply rate.

**Message:**
```
Hi Maggie — built something that's part-protocol, part-knowledge-work-for-agents: Polis Protocol. A folder of markdown files that lets Claude, Codex, and Gemini coordinate on the same project. Each agent has a capability card; work is bandit-routed by historical performance; high-stakes contracts get paired review before settlement.

The piece I'm most curious whether you'd find interesting is the amendment process — citizens can propose changes to the protocol itself, ratified amendments append to a constitution. The repo ships one real amendment changing routing rules after a lesson got filed.

Repo: https://github.com/yehudalevy-collab/polis-protocol

(Took inspiration from chavruta — paired Talmudic study — for the high-stakes review affordance. Wondering if that framing reads as too cultural-specific or as a useful anchor.)
```

**Why this works:** Maggie has tweeted about Talmudic-study-style review patterns; calling that out shows you've done your reading. Frame-question at the end invites a reply.

---

### 1.3 Sam McAllister (@sam_mcallister) or whoever runs Claude Code social

**Why:** Whoever is currently the public face of Claude Code on Twitter has access to the @AnthropicAI retweet pipeline. A retweet from them = 50k+ qualified eyes.

**Message:**
```
Hi Sam — Polis Protocol just shipped. It's a markdown coordination layer that turns Claude Code, Codex, and Gemini CLI into one team on the same project. Packaged as a Claude Code skill — drop it in ~/.claude/skills/polis-protocol and the bridge files for Codex/Gemini are auto-generated.

The interesting demo: a worked example where Claude was originally the leader on the "spanish-translation" tag, then ceded that role to Gemini after a chavruta-review lesson called madrij-not-líder was filed. The protocol *learned* and re-routed.

Repo: https://github.com/yehudalevy-collab/polis-protocol

If Claude Code's social account is looking for a community-built skill worth boosting, this might fit. No expectation either way — just sharing.
```

---

## Tier 2 — High-signal adjacent voices (NOT Anthropic, but their endorsement = Anthropic attention)

### 2.1 Simon Willison (@simonw)

**Why:** Probably the single most influential voice in practical LLM tooling. Writes about new tools daily on his blog. If he writes a 200-word note on Polis, it lands.

**Message:**
```
Hi Simon — built a markdown coordination layer for multi-vendor agent teams: Polis Protocol. Lets Claude Code + Codex + Gemini work as one team on the same project, with capability cards, bandit-routed contracts, and a ratifiable amendment process.

The bit I think you'd find interesting: every routing decision is explainable. `route_contract.py --explain` prints the score breakdown table for every candidate citizen. The audit trail is git-native.

Repo: https://github.com/yehudalevy-collab/polis-protocol
Worked example with three real citizens and a recorded routing leader-shift: examples/research-team/

(Not asking for a writeup — just figured this is the kind of thing you'd want to know exists.)
```

**Why this works:** Simon explicitly says he prefers DMs that share things rather than pitch them. The "not asking for a writeup" line is genuine, removes pressure, and ironically makes a writeup more likely.

---

### 2.2 Shawn Wang / swyx (@swyx)

**Why:** Latent Space podcast. Single biggest podcast in AI engineering. Knows the multi-agent space cold.

**Message:**
```
Hi swyx — open-sourced Polis Protocol today. A markdown-only coordination protocol for multi-vendor AI agent teams. Capability cards + ε-greedy bandit routing that learns from settled contracts + chavruta paired review + ratifiable amendments.

The framing I'm pitching: this is the coordination layer for the MCP era. MCP is connectivity (tools-to-agents); Polis is coordination (agents-to-agents). They compose, they don't compete.

Repo: https://github.com/yehudalevy-collab/polis-protocol

I'd love to write a guest post on "communication is the floor — the team gets better above it" for Latent Space if there's interest. Otherwise just sharing.
```

**Why this works:** Names a specific essay angle (`communication is the floor`) that swyx tweet-tested 3 months ago. Direct guest-post pitch is allowed because swyx accepts them.

---

### 2.3 Nathan Lambert (@natolambert) — Interconnects

**Why:** Best-in-class technical writer on RL and routing. Polis's bandit-routing math is in his wheelhouse.

**Message:**
```
Hi Nathan — built Polis Protocol. An ε-greedy multi-armed bandit routes contracts to AI agents from different vendors (Claude, Codex, Gemini) based on confidence-weighted historical scores per tag, exploring 15% of the time. Settled contracts ship lessons that update the routing stats.

The piece I'm specifically curious about: should the exploration rate auto-scale based on contract throughput? At low volume, 15% exploration burns too much signal. At high volume, 15% may not be enough. Considering switching to UCB1 for a v0.3.

Routing math reference: https://github.com/yehudalevy-collab/polis-protocol/blob/main/references/routing.md
Repo: https://github.com/yehudalevy-collab/polis-protocol

If you ever cover agent-team routing on Interconnects, this might be a useful real-world reference.
```

**Why this works:** Pitches the technical question Nathan likes to answer. UCB1 mention shows you know the landscape.

---

## Tier 3 — Community voices (use only if Tier 1/2 doesn't activate)

### 3.1 Twitter accounts to consider after Tier 1/2

- Latent Space podcast guests who've discussed agent infra recently (Andrej Karpathy, Jeremy Howard, Maxime Labonne)
- Continue.dev founders (they care about multi-tool workflows)
- Open Interpreter team
- A CrewAI maintainer (frame as complementary, not competitive)

Don't pre-write these — by the time you reach Tier 3 you'll have feedback from Tier 1/2 that should shape the message.

---

## Tracking

For each DM sent, log:
- Date sent
- Recipient
- Reply (yes/no, date)
- Outcome (retweet, quote, blog mention, podcast invite, ignored)

A 10% reply rate is a normal benchmark. A 25%+ reply rate means your messaging is tuned; a 0% reply rate after 5+ DMs means the messaging needs rewriting before continuing.

## What you're hoping for

In rough order of value:
1. A retweet or quote-tweet from any Tier-1 voice
2. A 200-word blog note (Simon Willison's preferred medium)
3. A podcast invitation
4. A "we should chat" reply (relationship-opening)
5. Any reply at all (signal you've registered on their radar)

Even ignored DMs have a delayed payoff — these people often see the project name a second time later (in their feed, in an awesome-list, in a colleague's share) and the prior DM primes recognition.
