# X / Twitter launch thread (4 tweets)

## Tweet 1 (the hook — must stand alone)

> Most multi-agent AI setups share a CLAUDE.md and hope.
>
> That solves "how do agents talk."
>
> It doesn't solve "who should do what," "is the team getting better," or "what if the rules are wrong."
>
> Polis Protocol does. Open source, markdown-only, vendor-agnostic.
>
> [attach: banner.png OR a 20–30s screen recording of init → contract → route → settle]

## Tweet 2 (the "before / after")

> The diff vs. a shared scratchpad:
>
> 🔹 Every agent publishes a signed capability card (vendor, model, tags, self-ratings)
> 🔹 Tasks are structured contracts routed by a learning bandit
> 🔹 Settled contracts produce lessons that update routing
> 🔹 Citizens can vote to amend the protocol itself
>
> Communication is the floor. The team gets better above it.

## Tweet 3 (the proof — code snippet)

> Concrete: here's a contract being routed in a real polis.
>
> Three citizens (Claude / Codex / Gemini). The router picks Gemini for Spanish translation because she has the best track record on `cultural-vocabulary-judaism`, not because the user happened to open her tab.
>
> [attach: code screenshot or a snippet like:]
>
> ```
> $ python route_contract.py --polis-root _polis \
>     --contract _polis/contracts/open/parent-newsletter-issue-3.md \
>     --explain
>
> Recommendation: gemini-translator-pesaj  (score=0.612, leader on this tag since April)
> ```

## Tweet 4 (the CTA)

> Vendor-agnostic by design — works across Claude Code, Codex, Gemini CLI, GPT, anything that reads markdown.
>
> MIT license. Worked example with three citizens, a leader shift, and a ratified amendment in the repo.
>
> 👉 github.com/yehudalevy-collab/polis-protocol
>
> Feedback and amendment-proposals very welcome.

---

## People to tag in replies (NOT in tweet 1 — keeps it clean and discoverable)

After the thread is live, reply-tag with a 1-sentence pitch:

- @swyx — Latent Space; he writes about agent protocols and multi-agent
- @hwchase17 — LangChain; multi-agent angle
- @joaomdmoura — CrewAI author; direct comparison opportunity
- @simonw — Simon Willison, evaluates LLM tools rigorously
- @jeremyphoward — fast.ai; appreciates simple, opinionated tools
- @AnthropicAI — they signal-boost Claude Code skills
- @AGI_Edgerunners, @LangChainAI, @llama_index — broader agent audiences

## Variant for LinkedIn (if posting there)

LinkedIn rewards problem-led posts more than tool-led. Open with:

> Three months ago I had a frustrating realization. I was running three AI assistants — Claude for research, Codex for code, Gemini for translation — on the same project. They had no idea what each other was doing.
>
> Worse: when one of them learned something useful, the others had no way to find out. Every session started from the same baseline. The team wasn't getting better.
>
> So I built Polis Protocol.
>
> [paste tweet 2's bullets]
>
> Open source under MIT. Link in comments.
