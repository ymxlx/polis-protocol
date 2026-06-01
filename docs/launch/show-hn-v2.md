# Show HN resubmit (v2 — story-led)

**Why a v2:** The first submission drew real traffic (HN was the #1 referrer in the
repo's first two weeks: ~280 unique clones, 60+ unique visitors) but didn't catch
fire. Diagnosis: the post led with the *taxonomy* (capability cards, bandit, amendments)
instead of the *thing that makes it click*. This version leads with the concrete
leader-shift and a one-command demo, and only then names the machinery.

HN etiquette: a resubmit is fine when the first didn't gain traction, especially with
a material change (now there's a 30-second runnable demo + GIF). Don't resubmit more
than once. Space it 3–4 weeks from the first attempt.

---

## Title (pick one — under 80 chars)

**Recommended (story-led):**
> Show HN: My AI agents re-routed work between vendors because they learned who's best

Alternates:
> Show HN: Polis – the router moved translation from Claude to Gemini because it learned
> Show HN: A markdown protocol where AI agents from 3 vendors learn who should do what

## URL field

`https://github.com/yehudalevy-collab/polis-protocol`

## Text field (the body of the post)

> I run three AI agents on the same projects — Claude for research, Codex for frontend, Gemini for translation. The recurring annoyance: a task lands on whichever agent's tab I happen to have open, not the one that's actually best at it. And when one of them learns something, the others never find out.
>
> So I built Polis Protocol: a folder of markdown files that turns those agents into a small "city" where work is routed by track record, and track record updates from outcomes.
>
> The moment it clicked for me: early on, Claude got most Spanish-translation tasks because it rated itself highly. After two finished contracts and one lesson ("the corporate word 'líder' reads wrong here; use the movement loan-word 'madrij'"), the router quietly started sending that work to Gemini instead. I didn't reassign anything. The team learned and the routing followed.
>
> You can watch that exact moment in one command, no install, no API keys:
>
>     git clone https://github.com/yehudalevy-collab/polis-protocol.git
>     cd polis-protocol && bash scripts/demo.sh
>
> Under the hood it's three things on top of a shared-file "floor": signed capability cards (who can do what), an ε-greedy bandit router (who should do this one, by history + self-rating + cost + availability), and ratifiable amendments (when a rule stops working, citizens vote to change the protocol itself). Vendor-agnostic — anything that reads markdown can join. No server, no runtime, ~400 LOC of Python per script.
>
> Worked example with the full leader shift and a real amendment: https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team
>
> MIT. I'd love feedback on the routing math and whether the self-amending-protocol idea holds up under real use — that's the part I'm least sure about.

## First comment (post within 30 seconds of submitting)

> Author here. Three things I cut from the post for length:
>
> 1. **Why a bandit and not an LLM router.** The routing decision is small and needs to be *explainable and cheap* — you run it on every contract. `route_contract.py --explain` prints the score breakdown for every citizen (history 55% / self-rating 20% / cost 15% / availability 10%), so you can always see why someone won. An LLM-as-router is more flexible but you lose the audit trail and pay tokens per decision. The math is small enough to also run as a reasoning step inside an agent's context if you'd rather.
>
> 2. **What "self-improvement" concretely means.** After a contract settles, the owner files a structured lesson keyed to capability tags; `--reconcile` folds it into `routing_stats.yml`. So next week's contract with the same tags routes differently from last week's. It's not autonomy — it's bookkeeping that compounds.
>
> 3. **The part I'm unsure about: self-amending rules.** Any citizen can propose a change to the constitution; a majority of active citizens ratifies it. The example repo has a real one (trivial `quality_impact: 1` lessons were polluting routing averages, so the team voted to floor influence at `quality_impact >= 3`). Open question I'd love HN's take on: does letting the protocol mutate per-project create more value (fits reality) or more chaos (every fork diverges)? My bet is the former, but it's a bet.
>
> Happy to go deep on any of it.

## Timing & execution

- Tuesday or Wednesday, 8:30–10:00 AM ET. Never Friday/weekend.
- First comment ready in another tab; post within 30 seconds.
- Block 4 hours. Reply to every top-level comment within ~10 minutes, concretely, linking to the specific repo file when relevant.
- When someone reports a real bug: thank them, file the issue quoting them, link it back. Visible responsiveness is the whole game on HN.
- If it catches, post the recap that evening to your X/LinkedIn ("Show HN went up, here's what people pushed back on").
