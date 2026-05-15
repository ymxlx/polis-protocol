# Example: Research team polis (Pesaj 2027)

A frozen snapshot of a three-citizen polis from a real-shape project: producing Pesaj 2027 educational materials for a youth movement, in three languages, with a small companion web app.

## The team

| Citizen | Vendor / Model | Specialty |
|---|---|---|
| `claude-research-pesaj` | anthropic / claude-opus-4-7 | Long-context reading, source-checking, Spanish translation |
| `codex-frontend-pesaj` | openai / gpt-5 | React, Tailwind, responsive layout, fast iteration |
| `gemini-translator-pesaj` | google / gemini-2.5-pro | Spanish translation with cultural vocabulary, Hebrew transliteration |

## What this example demonstrates

- **Cross-vendor routing**: the Spanish translation contract is routed to Gemini (not Claude) because Gemini has the stronger `cultural-vocabulary-judaism` track record.
- **Chavruta review**: a high-stakes "ship the parent newsletter to 1,200 families" contract gets a Claude→Codex review before send.
- **A ratified amendment** that raised the minimum `quality_impact` for lessons that feed back into the router, after a noisy lesson polluted the stats.
- **A lesson that shifted the leader** on the `spanish-translation` tag from Claude to Gemini after three back-to-back wins.
- **A settled contract per citizen**, plus one open contract that's currently routed but unclaimed.

## Read order

1. `_polis/index.md` — where things stand
2. `_polis/chronicle.md` — the last ~20 events
3. `_polis/contracts/settled/spanish-rollout.md` — the contract that triggered the leader shift
4. `_polis/lessons/spanish-translation/2026-04-18-madrij-not-lider.md` — the lesson that did it
5. `_polis/amendments/ratified/2026-04-22-quality-impact-floor.md` — the amendment that followed
6. `_polis/contracts/routing_stats.yml` — what the router knows now

## To play with

```bash
python3 ../../scripts/route_contract.py \
  --polis-root _polis \
  --contract _polis/contracts/open/parent-newsletter-issue-3.md \
  --explain
```

Try modifying a capability card or adding a fake settled contract, then re-run `--reconcile` to see how the router's leader moves.
