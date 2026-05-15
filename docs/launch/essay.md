# Communication is the floor. The team gets better above it.

*Or: why a multi-agent protocol that only enables note-passing leaves most of the value on the table.*

---

When people set up two AI agents to work on the same project, the first instinct is to give them a shared file. A `CLAUDE.md`. An `AGENTS.md`. A Notion page. Now they can leave each other notes. They can hand off. They can stop overwriting each other's work.

This is good. This is also the floor.

Because at this point the protocol has answered one question — *how do agents communicate?* — and left three more on the table:

1. **Who should do what?** Tasks land on whichever agent happens to be the user's current session. A frontend question goes to Claude because Claude is open in the chat window, not because Claude is better at frontend than the Codex session sitting idle in another tab.
2. **Does the team get better over time?** Each session starts from the same baseline. Lessons don't compound. The third time the team gets bitten by the same edge case, no one notices it's the third time.
3. **What happens when the protocol itself is the problem?** Rules that worked at the start chafe under real use. There's no path from "this rule keeps causing friction" to "the rule has been updated."

`agent-vault`, my own previous attempt, sat exactly at the floor. So do the AGENTS.md conventions. So do most "shared scratchpad" setups. They optimize for *not stepping on each other*. They don't optimize for *the team getting better*.

**The Polis Protocol** is what happens when you treat communication as the baseline and ask, what stacks on top?

## Three institutions on top of the floor

Polis is named for the small Greek city: a few thousand citizens who all know each other and run their own affairs. The mapping is direct.

**The Register.** Every agent is a citizen, and every citizen publishes a signed capability card. Vendor, model, languages, capability tags with self-ratings, cost envelope, latency envelope, standing instructions. The card is the polis's answer to "who can do what." No central directory; no permission needed to join. New tools just write their card and start participating.

**The Contract.** Tasks are not free-form. They are three-section markdown files: Intent (goal, acceptance criteria, required capability tags, stakes), Assignment (owner, plan, estimated effort), and Settlement (outcome, quality self-score, what bit, lesson reference). Open contracts live in `contracts/open/`; settled ones move to `contracts/settled/` and never get deleted.

**The Chronicle and the Lessons.** A line per meaningful action lands in an append-only `chronicle.md`. A settled contract produces a structured lesson, filed by capability tag, that future citizens read before taking similar work. The chronicle records what happened; the lessons record what was *learned*. Most events are not lessons, and most lessons distill many events.

**The Amendment.** When a rule stops working, any citizen can propose a change. Other citizens vote. When a simple majority of active citizens agree, the file moves to `amendments/ratified/` and the constitution itself is edited. The protocol updates itself.

## Where the work goes: a learning bandit

Communication is solved by the chronicle. Optimization is solved by the router.

When a contract is opened with required capability tags, the router scores every citizen as a weighted combination of historical performance on those tags (55%), self-rating (20%), cost fit (15%), and current availability (10%). Most of the time it picks the top-scored citizen (exploit). Some of the time (15%) it picks a non-top one weighted by score (explore), so the policy stays honest about whether the current leader is still actually best.

When a contract settles, `routing_stats.yml` updates with the new quality score. That update is the team getting better. Not in the abstract — in the literal sense that next Tuesday's Spanish-translation contract will be routed differently from last Tuesday's, because the team learned something in between.

The router is a 60-line Python script. You can also run it as a reasoning step inside any agent's session; the math is small enough to do in context. Both produce the same answer.

## How the team develops

Two real moments from the [research-team example](https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team):

**A leader shift.** Early in the project Claude routed itself most Spanish translation contracts on the strength of self-rating. After two settled contracts and one high-impact lesson ("the Hispanic-corporate word 'líder' reads wrong; use the movement loan-word 'madrij'"), Gemini overtook Claude on the `spanish-translation` tag and started getting routed work. Nobody told the router. The router noticed.

**An amendment.** Six weeks in, the team observed that `quality_impact: 1` lessons — trivial fixes, library quirks — were dragging the routing stats around. Gemini's effective historical score on `spanish-translation` was *below* her actual quality scores because two trivial lessons under her name were polluting the average. Codex proposed an amendment that floored `quality_impact >= 3` for routing influence. Claude and Gemini voted yes. The rule changed. The next reconcile cleaned the stats.

Neither of these is dramatic. That's the point. The dramatic version of multi-agent coordination — autonomous swarms, master agents, self-organizing hives — has been pitched in slide decks for two years and shipped in approximately zero production systems. What ships is small teams of agents that mostly stay out of each other's way and occasionally do something useful together. The interesting question is not how to make those teams more autonomous. The interesting question is how to make them *learn*.

## Protocols that learn beat protocols that prescribe

Most multi-agent protocols are frozen at design time. Their authors anticipate the failure modes, write rules to prevent them, and ship. When real use surfaces a failure mode the authors didn't anticipate, the team's options are: ignore the rule, fork the protocol, or wait for v2.

Polis bets the other way. The protocol *itself* is one of the things the team can change. The constitution lives in the project, not in the skill. Amendments are voted on by the citizens who actually run into the friction. The default rules in the skill are a seed; over time a given polis will diverge in small ways that fit its project. That divergence is the feature.

This is a different relationship between protocol-author and protocol-user. I (the author) am claiming less. I'm shipping a starting point and a mechanism. You (the user) are not constrained to the starting point. The constitution is *yours*.

## The bet

Three claims, in order of how confident I am:

1. **Multi-vendor teams beat single-vendor teams** on most non-trivial projects, because different vendors have different blind spots and the union covers more ground than any one model.
2. **A learning router beats a fixed assignment policy** on any project long enough that the team's relative strengths actually emerge from data rather than self-assessment.
3. **A self-amendable protocol beats a frozen one** on any project long enough that the original rules will, at some point, get in the way.

If those three are right, then a protocol that bakes them in — the way Polis does — should beat both the "free-form shared scratchpad" floor and the "single-vendor framework" ceiling on real work over real time. That's the bet.

Try it on something small. A weekend project with two agents. See what the chronicle looks like at the end of day three. Then come tell me if the protocol got in the way.

—

*Polis Protocol is open source under MIT. Repo: [github.com/yehudalevy-collab/polis-protocol](https://github.com/yehudalevy-collab/polis-protocol). Issues and amendment proposals welcome.*
