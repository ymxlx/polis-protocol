# Community pitches

One-shot copy you can paste into each channel. Each is tuned to its venue.

---

## r/LocalLLaMA

**Title:** Polis Protocol: a markdown-only coordination protocol where multi-vendor AI agents route work to whoever's best at it

**Body:**

> I built this after getting frustrated that my Claude, Codex, and Gemini sessions had no idea what each other were doing on shared projects.
>
> It's a folder of markdown files plus two Python scripts. Every agent publishes a signed capability card. Tasks are structured contracts. A multi-armed bandit routes contracts to whichever citizen has the best historical score on the required tags, explores 15% of the time to keep learning. Settled contracts file structured lessons that update `routing_stats.yml`. Citizens can propose and vote on amendments to the protocol itself.
>
> Vendor-agnostic. Works with any LLM tool that reads markdown — Claude Code, Codex, Gemini CLI, Ollama-based local agents, etc.
>
> Worked example with 3 citizens, a leader shift on a tag after a high-impact lesson, and a ratified amendment:
> https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team
>
> Repo: https://github.com/yehudalevy-collab/polis-protocol
>
> Happy to answer questions about the bandit math, the chavruta-review mechanism for high-stakes contracts, or how it compares to AGENTS.md and CrewAI.

---

## r/AI_Agents

**Title:** Open-sourced a multi-agent coordination protocol with bandit routing + self-amending rules

**Body:** (same as r/LocalLLaMA but lead with "I needed agents from different vendors to know what each other were doing on a long project")

---

## r/MachineLearning (Weekly Project Thread only — Rule 5)

**Title:** [P] Polis Protocol — vendor-agnostic multi-agent coordination with ε-greedy bandit routing and self-amending constitution

**Body:** (more technical — emphasize the routing math, the confidence-weighted historical scoring, and the explore/exploit trade-off; link to `references/routing.md`)

---

## Hacker News (Show HN)

See `show-hn.md` in this folder.

---

## Lobste.rs (need invite)

**Tags:** `ai`, `distributed`, `practices`
**Title:** Polis Protocol: markdown-based coordination for multi-vendor AI agent teams

(Short, factual, link-led — Lobste.rs prefers terse to flashy.)

---

## Dev.to / Hashnode (48 hours after HN, cross-posted)

Use `essay.md` from this folder. Add a canonical link tag pointing at your own site if you mirror it there first.

---

## Discord channels (post in #show-and-tell or #projects, not #general)

Each gets a tailored 2-sentence intro. Below: the channels and the angle.

**LangChain Discord** (`#projects`):
> Built a vendor-agnostic multi-agent protocol with bandit routing and lessons that update the policy on settlement. Specifically curious how LangGraph users would feel about adopting it as the coordination layer underneath a LangGraph workflow.

**LlamaIndex Discord**:
> Vendor-agnostic multi-agent coordination protocol; works alongside LlamaIndex agents as a routing + learning layer. Worked example in the repo. Feedback welcome.

**AI Engineer Foundation Discord**:
> Multi-vendor agent protocol. Markdown-only, bandit routing, self-amending. MIT-licensed. Curious whether this fits anyone's stack.

**Anthropic Builders / Claude Code community**:
> Packaged as a Claude Code skill. Adds capability cards, contract-based routing, and chavruta review for high-stakes contracts to whatever your Claude Code session is doing. Also writes bridge pointers for Codex / Gemini so the polis works across tools.

**Cognition / Devin community** (if accessible):
> Coordination protocol for teams of agents from different vendors. Devin is the obvious "execution" citizen; pairing with a Claude or Gemini review citizen via chavruta-review is exactly the use case Polis was designed for.

---

## Newsletter pitches (3 sentences each — email directly)

### Latent Space (swyx@latent.space)

> Subject: Polis Protocol — a multi-vendor agent coordination layer that *learns*
>
> Hi swyx, big fan. I just open-sourced Polis Protocol — a markdown-only coordination layer for multi-vendor AI agent teams (Claude + Codex + Gemini + anything else that reads markdown). The differentiator vs. AGENTS.md / CrewAI is that work is routed by a multi-armed bandit using settled-contract performance, and citizens can vote to amend the protocol itself when rules stop working. Worked example with three citizens and a leader shift in the repo: https://github.com/yehudalevy-collab/polis-protocol — happy to write a guest post on "communication is the floor" if there's interest.

### Ben's Bites (ben@bensbites.com)

> Subject: Open-sourced: AI agents from different vendors that learn who to assign work to
>
> Hi Ben, I shipped Polis Protocol today — open-source MIT, markdown-only, lets Claude + Codex + Gemini work as one team on a project with a learning router that figures out who's best at what over time. Worked example in the repo with three real citizens and a documented leader shift after a lesson. Repo: https://github.com/yehudalevy-collab/polis-protocol — would love a mention if it fits.

### TLDR AI (tldr@tldrnewsletter.com)

> Subject: Polis Protocol — vendor-agnostic multi-agent coordination, open-sourced
>
> Hi, just launched Polis Protocol: a markdown coordination protocol for AI agent teams across vendors (Claude, Codex, Gemini, GPT). Features signed capability cards, multi-armed-bandit routing, self-improving via settled-contract lessons, and a ratifiable amendment process for the protocol itself. Open source MIT, repo at https://github.com/yehudalevy-collab/polis-protocol — happy to provide a 50-word summary in your format.

### AlphaSignal (lior@alphasignal.ai)

> (same shape as TLDR AI, slightly more technical — emphasize the bandit math)

### The Neuron (pete@theneurondaily.com), The Rundown AI

> (broader audience — lead with the "AI agents that get better as a team" angle, not the technical details)

### Interconnects (Nathan Lambert)

> Nathan tends toward technical posts on RL and routing. Pitch the bandit-as-routing angle and the self-amending governance question.

### Import AI (Jack Clark)

> Jack writes about agent governance and capability. Pitch the *amendment mechanism* as the angle — "what does it look like for a protocol to update itself?" — and offer the worked example.

---

## What NOT to do

- Don't cross-post within 24 hours across r/LocalLLaMA, r/AI_Agents, r/MachineLearning. Stagger by 48h+.
- Don't reply with the same canned text on different Discords. Tailor the lead sentence.
- Don't tag big names in tweet 1. Reply-tag them after the thread is up.
- Don't post on Friday afternoon or weekends (HN especially).
