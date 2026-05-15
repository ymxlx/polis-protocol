# Seven-day launch checklist

Three rules through all of it: **respond fast, ship visibly, credit by name.**

---

## Day –1 (evening before launch)

- [ ] **Upload social preview image** to GitHub: Settings → Social preview → upload `assets/banner.png`. *(API-only; only you can do this.)*
- [ ] **Record a 20–30s demo GIF**. Best path: terminal recording of `init_polis.py` → opening a contract → `route_contract.py --explain` → settling. Use `asciinema rec` then `agg` for the GIF, or Loom + ffmpeg, or [terminalizer](https://terminalizer.io/). Drop into `assets/demo.gif` and reference it at the top of the README.
- [ ] **Confirm CI is green** — `https://github.com/yehudalevy-collab/polis-protocol/actions`. If the badge is red, fix before launch.
- [ ] **Pin the launch tweet draft** in a Notion / scratch file so you can paste it fast Tuesday morning.
- [ ] **Open all browser tabs you'll need**: HN submit, X compose, r/LocalLLaMA submit, r/AI_Agents submit, Discord servers, gmail with newsletter pitch threads drafted.

## Day 1 — Launch day (Tuesday or Wednesday, 8:30 AM ET)

**Hour 0 (8:30 AM ET):**
- [ ] Submit Show HN (`docs/launch/show-hn.md` body). Within 30 seconds, post the first comment from `show-hn.md`.
- [ ] Send tweet 1 of the X thread. Then 2, 3, 4 spaced ~30s apart so they thread cleanly.
- [ ] Submit to r/LocalLLaMA (pitch from `community-pitches.md`).

**Hour 1:**
- [ ] Submit to r/AI_Agents.
- [ ] Send the 6 newsletter pitch emails from `community-pitches.md`. One per send — don't bcc.
- [ ] Post to 4 Discord servers (LangChain, LlamaIndex, AI Engineer Foundation, Anthropic Builders). Tailored lead sentence each.

**Hours 1–5:**
- [ ] **Stay at the keyboard.** Reply to every HN comment within 10 minutes. Every Reddit comment within 30 minutes. Every Discord question same-day.
- [ ] When you respond, **link to a specific file in the repo** when relevant. Specificity beats summary.
- [ ] Reply-tag (don't quote-tweet) the 5–7 people from `x-thread.md` with 1-sentence pitches. Use the language of *their* recent posts.

**Evening:**
- [ ] Pin the HN URL to your X profile.
- [ ] Post a recap thread reply: "Day 1 in: ⭐ stars, 💬 comments, 🪲 issues filed. Top feedback: X, Y, Z."

## Day 2–3

- [ ] **Publish the launch essay** (`docs/launch/essay.md`) to your domain (or pitch as a Latent Space guest post — DM swyx). Then mirror to Dev.to + Hashnode after 48h with canonical link tag.
- [ ] **Lobste.rs submission** (if you have an invite). Tags: `ai`, `distributed`, `practices`.
- [ ] **DM 10 specific agent builders** asking for honest feedback (NOT stars). People who actually run multi-agent setups — that's who can give useful critique. Names from the AI Engineer community, CrewAI Discord, and Claude Code Discord are good starts.
- [ ] **File 5 "good first issue" tickets** so drive-by contributors have an on-ramp. Examples: "Add an Aider bridge pointer", "Add `--dry-run` flag to `init_polis.py`", "Build the `product-team` example", "Add UCB router variant", "Add asciinema demo to README".
- [ ] If a comment surfaced a concrete bug, **ship a v0.1.1 fix the same day** and link it back to the commenter ("@x flagged this on HN, fixed in 4f3a92e — thanks").

## Day 4–5

- [ ] **Write the follow-up post**: *"What 72 hours of feedback taught Polis Protocol."* Be honest about pushback you got. This is where compounding starts; the follow-up post often outperforms the launch post because it has a built-in audience of people who already saw the launch.
- [ ] Cross-post the launch essay to Dev.to + Hashnode with canonical link.
- [ ] Apply to **AI Engineer Summit / AI Engineer World's Fair CFP** with a "lessons from designing a self-amending protocol" talk angle. (Even if it's not accepted, the application is a CFP-friendly version of the essay.)

## Day 7

- [ ] **Ship v0.2** incorporating one specific piece of feedback. Tag the commenter in the release notes by name. Tweet the release.
- [ ] **Apply to Latent Space podcast** with a clip from the X thread.
- [ ] **Awesome-list PR follow-up**: check status of the awesome-claude-code, awesome-agents, awesome-multi-agent-systems PRs. Comment politely if they've stalled.
- [ ] **Anthropic plugins marketplace**: submit the PR to `anthropics/claude-plugins-official` if not done on Day 0.
- [ ] Write Day-7 retrospective: stars, forks, real-world adoption signals, issues filed by non-author, awesome-list landings. Post as a tweet thread.

---

## What to skip

- LinkedIn launch (low dev signal).
- Product Hunt (wrong audience for protocols).
- Paid promotion of any kind.
- "Awareness" posts that don't include a concrete code snippet or example.

## What success looks like

- **Day 1**: ≥ 50 HN points OR ≥ 100 Reddit upvotes OR ≥ 1 newsletter inclusion.
- **Day 3**: ≥ 1 unsolicited PR or issue from a non-author.
- **Day 7**: ≥ 1 awesome-list inclusion landed, ≥ 1 fork that actually uses Polis on a real project (check the chronicle.md files in forks).
- **Day 30**: ≥ 1 mention in a podcast / newsletter / write-up you didn't pitch.
