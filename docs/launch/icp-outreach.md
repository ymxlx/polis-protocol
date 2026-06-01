# ICP outreach kit — find the people who already have this pain

The data says people *arrive and clone* (≈280 unique clones in two weeks) but few
convert to vocal supporters. Broadcasting more won't fix that. Going **one-to-one**
with people who are *already complaining about the exact problem* will.

This is a daily 15-minute habit, not a campaign. Goal per day: **3 genuinely useful
replies** to real people. Not 30 copy-pastes. Three good ones.

---

## Who the ICP actually is

The narrow set who feel this pain *today*:

1. People running **2+ coding agents from different vendors** on one project (Claude Code + Codex, + Cursor, + Gemini CLI) and complaining they don't coordinate.
2. People frustrated that **work lands on the wrong agent** / they manually shuttle context between agents.
3. People building **multi-agent orchestration** who've hit the "it works until I add a non-framework agent" wall.
4. People asking **"how do I make my agents share memory / not repeat mistakes."**

Not the ICP (don't waste replies): single-agent users, people who want autonomous swarms, people who want a GUI product.

---

## Where to find them (search these, daily)

**X / Twitter** (search, sort by Latest):
- `claude code codex (coordinate OR coordination OR "talk to each other")`
- `("multiple agents" OR "multi-agent") (mess OR messy OR chaos OR "step on")`
- `cursor "claude code" same project`
- `gemini cli codex claude (workflow OR juggle OR switch)`
- `"AGENTS.md" (wish OR limitation OR "doesn't")`

**Reddit** (search across r/ClaudeAI, r/LocalLLaMA, r/AI_Agents, r/ChatGPTCoding):
- `multi-agent coordination`
- `claude codex gemini together`
- `agents repeat mistakes` / `agents shared memory`
- Sort by New; reply while the thread is still warm (<12h old).

**Hacker News** (hn.algolia.com, last 24h):
- `multi-agent`, `agent coordination`, `AGENTS.md`
- Reply in-thread where someone describes the pain.

**GitHub** (issues/discussions):
- Issues on CrewAI, LangGraph, AGENTS.md-adjacent repos asking about cross-vendor or routing. A thoughtful "here's a different approach" comment (not a drive-by link) is welcome there.

---

## The reply playbook

**Rule 1 — lead with their problem, not your project.** Mirror their words back first.
**Rule 2 — show, don't tell.** Link the one-command demo, not the homepage.
**Rule 3 — one link max.** More than one reads as spam.
**Rule 4 — ask a real question.** It earns a reply and gives you feedback.
**Rule 5 — no copy-paste.** Each reply references their specific situation.

### Template A — someone complaining agents don't coordinate

> This is exactly the thing that bugged me — a task lands on whichever agent's tab is open, not the one best at it. I ended up building a tiny markdown protocol where each agent has a capability card and work gets routed by track record. You can watch it move a task from one vendor to another in one command (no install): `git clone … && bash scripts/demo.sh`. Curious what your setup looks like — how many agents, which vendors?

### Template B — someone frustrated agents repeat mistakes / no shared memory

> The "they never learn from each other" part is what got me too. The approach I landed on: every finished task files a one-line lesson keyed to a skill tag, and that updates who gets routed similar work next time. Small bookkeeping, compounds fast. 30-sec demo of the loop if useful: [link]. Does your pain show up more in *routing* (who does it) or *memory* (not repeating)? Genuinely asking — shaping v0.2.

### Template C — multi-agent framework user hitting the cross-vendor wall

> Ran into the same wall — frameworks are great until you want to add an agent that isn't in the framework. The thing that helped me was moving coordination *out* of any runtime into plain markdown both agents read. Wrote it up as a protocol here if it's useful: [link]. How are you handling the non-framework agent today?

### Template D — HN/Reddit thread, more technical audience

> Built something adjacent: an ε-greedy bandit routes contracts to whichever agent has the best history on the required tags, settled contracts update the stats, and you can `--explain` any decision to see the score breakdown. Vendor-agnostic, markdown-only. The routing math and a worked leader-shift example are in the repo. Would value a critique of the cold-start handling specifically.

---

## After someone engages

- If they try it: **ask for the friction**, not for a star. "What broke / what was confusing?" The answer is worth more than the star, and people who feel heard often star anyway.
- If they file a real bug: fix it fast, tag them in the commit/issue, tell them. One delighted early user → several referrals.
- If they're clearly an ideal user: invite them to open an issue with their use case so it's tracked publicly (turns a DM into durable, visible engagement).

## Track it

Keep a simple log (even a text file): date · who · their pain · your reply link · did they engage · outcome. After ~20 outreaches you'll see which template and which venue converts, and can double down.

## What good looks like

- Week 1: 1–2 real conversations, 1 piece of usable feedback.
- Week 2–3: 1 person who actually runs Polis on a real project and tells you what happened.
- That single real user is the unlock — they become the case study, the testimonial, and usually the first non-author contributor. Everything compounds from there.
