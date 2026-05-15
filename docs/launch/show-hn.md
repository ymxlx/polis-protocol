# Show HN draft

## Title (pick one — keep under 80 chars)

**Recommended:**
> Show HN: Polis Protocol – multi-vendor AI agents that learn who to route to

Alternates if A/B-testing:
> Show HN: Polis – a markdown protocol for AI agent teams that get better over time
> Show HN: Polis Protocol – capability cards, bandit routing, and lessons in markdown

## URL field

`https://github.com/yehudalevy-collab/polis-protocol`

## Text field (this is the body of the post, NOT a separate comment)

> Most multi-agent setups share a CLAUDE.md or AGENTS.md file and hope. That solves "how do agents communicate," but not "who should do what," "does the team get better over time," or "what happens when the protocol itself is the problem."
>
> Polis adds three institutions on top of the shared-file floor:
>
> - **Capability cards** — every agent publishes a signed YAML manifest of what it can do (vendor, model, tags with self-ratings, cost, latency).
> - **A learning bandit router** — tasks are structured contracts with required capability tags; the router scores every citizen on historical performance, self-rating, cost fit, and availability, exploits the top score most of the time, explores a non-top option 15% of the time, and updates `routing_stats.yml` when a contract settles.
> - **Ratifiable amendments** — when a rule stops working, citizens propose changes to the constitution and vote. The protocol updates itself.
>
> It's vendor-agnostic by design. The same polis can be shared by Claude Code, Codex, Gemini CLI, GPT, anything that reads markdown. There's no server, no required runtime, and the whole thing is one folder of `.md` files plus two Python scripts (~400 LOC each).
>
> Worked example with three citizens (Claude, Codex, Gemini), a leader shift on a tag after a high-impact lesson, and a ratified amendment: https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team
>
> MIT-licensed. Happy to dig into the routing math, the chavruta-review mechanism for high-stakes contracts, or how this compares to AGENTS.md / CrewAI / autogen.

## First comment to post yourself (right after submission)

> Some quick context I left out of the post for length:
>
> 1. **Why "polis."** Greek for a small city. The metaphor is sticky: agents are citizens, capabilities are public, tasks are contracts, the chronicle is the city's public record, and the constitution is the rulebook citizens can vote to amend. It's a more honest mental model than "swarm" or "framework" for what these small teams actually are.
>
> 2. **How this compares to AGENTS.md.** AGENTS.md is a great floor (and Polis writes one as a bridge pointer at the project root so Codex picks it up). Polis adds the three things on top: structured routing, lessons that compound, amendments. If you only need note-passing between two sessions, AGENTS.md is enough; Polis earns its keep when you have 3+ agents from different vendors and "who should do this" is a real question.
>
> 3. **The bandit math.** ε-greedy by default with confidence-weighted historical scores. Cold-start is handled by leaning on self-ratings until contracts accrue. The full routing reference is at `references/routing.md` in the repo. UCB and Thompson sampling variants are on the roadmap.
>
> 4. **What "self-improvement" really means here.** Concretely: after a settled contract, the owner files a structured lesson keyed to capability tags, and that lesson updates `routing_stats.yml` via `route_contract.py --reconcile`. So when next Tuesday's contract opens with the same required tags, the routing recommendation is different from last Tuesday's, because the team learned something in between. Not magical autonomy; just bookkeeping that compounds.
>
> Happy to answer specifics.

## Timing

- Post Tuesday or Wednesday, 8:30–10:00 AM ET. Avoid Mondays (slow) and Fridays (slow).
- Have the first comment ready in another tab so you can post within 30 seconds of submission. The first comment slot is high-attention real estate.
- Be at the keyboard for **at least 4 hours** after submitting. Reply concretely and fast to every top-level comment.

## Reply tactics

- **Skeptical comment ("isn't this overengineered?")**: agree with the spirit, then point at the worked example showing the smallest possible useful polis (2 citizens, 1 settled contract). Acknowledge that the floor cases don't need Polis.
- **Comparison comment ("how is this different from X?")**: name one concrete thing X doesn't do, link to the relevant file. Don't dunk on X.
- **Bug report in the comments**: thank, file an issue from your account quoting the comment, link the issue back. Visible responsiveness compounds.
- **"Tried it, didn't work" comment**: ask for the polis layout that broke. Offer to debug live. This is the highest-leverage interaction on HN.
