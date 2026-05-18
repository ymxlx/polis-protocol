# Anthropic Builders Showcase — application package

## Where to apply

- **Primary:** https://www.anthropic.com/builders (look for "Submit your project" / "Featured Builder" call-to-action)
- **Builders newsletter:** https://www.anthropic.com/news (often has Builder-feature announcements; reply to one if a direct submission form isn't visible)
- **Email fallback:** If no form is visible, send to `builders@anthropic.com` or `community@anthropic.com`

If the showcase application is locked behind a Workspaces account, sign in with the GitHub or Google account that owns the polis-protocol repo so the connection between the application and the repo is auto-verified.

---

## Pre-drafted application fields

### Project name
```
Polis Protocol
```

### One-sentence pitch
```
A markdown coordination protocol that lets Claude Code, Codex, and Gemini work as one team on the same project — with a multi-armed bandit that learns who's best at what, and an amendment process so the protocol itself evolves through use.
```

### Repository
```
https://github.com/yehudalevy-collab/polis-protocol
```

### Project category
```
Agent infrastructure / Multi-agent coordination / Open protocols
```

### Built with (Anthropic products used)
```
Claude Code (primary citizen / implementation lead)
Claude Sonnet 4.6 (chavruta paired review of high-stakes contracts)
Claude API (none directly — Polis is markdown-only, no SDK lock-in)
```

### What problem does it solve? (≤500 words)
```
When agents from different vendors work on the same codebase — Claude Code doing implementation, Codex doing review, Gemini handling translation — they have no shared state. Each session starts cold. Hardcoded AGENTS.md / CLAUDE.md / GEMINI.md files capture *intent* but never learn from *outcomes*. Multi-vendor teams either accept a fragile manual coordination layer or collapse back to a single vendor (losing the benefits of model diversity).

Polis Protocol solves this with three primitives in a folder of markdown files:

1. **Capability cards** — every citizen agent publishes a signed YAML card with tags, model, tool, throughput, and historical track record.
2. **Contracts** — every unit of work is a structured markdown contract with required tags, acceptance criteria, and a settlement note.
3. **Routing stats** — an ε-greedy multi-armed bandit picks the citizen with the best confidence-weighted score on the contract's tags, exploring 15% of the time. Settled contracts ship lessons that update the routing stats on the next reconcile.

Two governance affordances build on top:

- **Chavruta (paired) review** — any contract with `risk: high` automatically gets a second citizen assigned as reviewer before settlement.
- **Amendments** — citizens propose changes to the constitution itself; ratified amendments are appended (never overwritten) and update the rules of routing or review.

The protocol survives the only test that matters: a real routing decision changing because the team *learned* something. The repo ships a worked example (`examples/research-team/`) where Claude was originally the leader on the `spanish-translation` tag, then ceded that role to Gemini after a chavruta-review lesson called `madrij-not-líder` was filed.

Vendor-agnostic by design — works with any tool that reads markdown. No daemon, no database, no cloud dependency. Audit trail is git-native; every routing decision can be explained via `route_contract.py --explain`.

For Anthropic specifically: Polis positions Claude as a peer in a multi-vendor team, not a silo. The protocol's chavruta-review mechanism encodes the AI-safety pattern of "have AI agents review each other" as a first-class governance affordance, not an afterthought.
```

### Why this is interesting (≤300 words)
```
Three reasons:

First, it's a **protocol, not a product**. Most multi-agent work today is delivered as runtime libraries (CrewAI, LangGraph, AutoGen). Polis is a markdown spec plus a reference implementation. That positioning makes Anthropic's ecosystem more open, not more locked-in — which historically the Anthropic developer community has rewarded.

Second, it **encodes the chavruta-review pattern as governance**. The chavruta (Hebrew: paired-study) tradition has 1500+ years of empirical evidence that paired critical review produces better outcomes than solo work. Polis turns this into an automatic affordance for high-stakes contracts, which directly aligns with Anthropic's AI-safety messaging about "AI systems that supervise AI systems."

Third, it **survives first contact**. The amendment process means the protocol itself can change as users discover edge cases. This is the dream of self-amending governance applied to AI workflows. The worked example in the repo already shows one ratified amendment changing the routing rules in response to a routing-pollution problem.

If Anthropic features Polis in the Builders Showcase, the framing that works best for the broader narrative is: "this is what an open, vendor-neutral coordination layer looks like — built by a community member, MIT-licensed, on Claude." That framing also creates room for Anthropic to talk about Claude as the *first peer in the polis*, rather than the only agent.
```

### Open source?
```
Yes, MIT licensed.
```

### Status / Maturity
```
v0.1.0-alpha (May 17, 2026). CI green across Python 3.10–3.13. Worked example shipping. Already listed in 2 community awesome-lists; 12 more PRs awaiting maintainer review at the time of this application.
```

### Funding / Sponsorship
```
Self-funded. Not seeking funding — would love a featured slot to reach the right ICP.
```

### Has the project been featured anywhere yet?
```
- Submitted to anthropics/claude-plugins-official#1893 (auto-redirected to clau.de form)
- Submitted to clau.de/plugin-directory-submission (separately, as recommended)
- Listed in 2 awesome-lists: GetBindu/awesome-claude-code-and-skills, Chat2AnyLLM/awesome-repo-configs
- 12 more awesome-list PRs in maintainer review queues
- LinkedIn launch post + Show HN
```

### Links to demos / screenshots / videos
```
- README with banner: https://github.com/yehudalevy-collab/polis-protocol
- Worked example (research-team polis): https://github.com/yehudalevy-collab/polis-protocol/tree/main/examples/research-team
- Routing math reference: https://github.com/yehudalevy-collab/polis-protocol/blob/main/references/routing.md
- Sample chavruta review: https://github.com/yehudalevy-collab/polis-protocol/blob/main/examples/research-team/_polis/reviews/madrij-app-mvp-review.md
- A real ratified amendment: https://github.com/yehudalevy-collab/polis-protocol/blob/main/examples/research-team/_polis/amendments/quality-impact-floor.md
```

### How can we reach you?
```
GitHub: @yehudalevy-collab
Email: yehuda.moshe24@gmail.com
```

### Anything else?
```
If Anthropic's DevRel team has bandwidth to do a 15-minute call to validate the framing before featuring, I'd welcome that. Three specific points where outside perspective would help shape the v0.2 release:

1. Whether "chavruta review" is too cultural-specific a term for a broad audience (alternatives: paired-review, peer-review, dual-witness review).
2. Whether the amendment process should default to single-citizen ratification or multi-citizen quorum (currently single-citizen for simplicity; the example shows a 2-of-3 quorum amendment).
3. Whether to position Polis as a *Claude Code skill* (narrow, easier to feature) or a *vendor-neutral protocol* (broader, harder to feature). I lean toward the second framing but understand the showcase may prefer the first.
```

---

## Final checklist before submitting

- [ ] Refresh `https://www.anthropic.com/builders` (the showcase form sometimes moves; if it's not visible, try `https://www.anthropic.com/community` or the Claude developer site)
- [ ] Sign in with the GitHub account `yehudalevy-collab` so the repo connection is automatic
- [ ] Have the README open in another tab so any link-the-form-asks-for is fast to copy
- [ ] Submit Monday or Tuesday mornings — DevRel inboxes are clearer then

## Realistic expectation

The Builders Showcase reviews on a slower cadence than the plugin directory. Typical timeline: 30–90 days to first response. If accepted, featuring usually happens within 2 weeks of acceptance.

If declined: there's almost always a useful reason in the rejection email. Don't take it as final — projects sometimes get a second look 3–6 months later after they've accumulated more adoption signal.
