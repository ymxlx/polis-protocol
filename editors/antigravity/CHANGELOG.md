# Changelog

## 0.1.2

- Fix the Activity Bar icon rendering as a solid square. The view container now uses a dedicated transparent monochrome SVG mark (the colored badge is kept for the marketplace listing).

## 0.1.1

- New brand icon: a hexagonal "polis" of connected citizen-nodes around a glowing central router. Replaces the placeholder banner crop.

## 0.1.0

Initial release.

- Polis sidebar: open contracts, citizens, and quick actions.
- `Polis: Found a polis` — scaffold `_polis/` and register the current Antigravity agent as a citizen.
- `Polis: Install skill into Antigravity (global)` — install the Polis `SKILL.md` into `~/.gemini/antigravity/skills/`.
- `Polis: Install skill into this workspace` — install into `.agents/skills/`.
- `Polis: Route an open contract (explain)` — run the learning router with a full score breakdown.
- `Polis: Open CONSTITUTION.md`.
- Status bar item showing the open-contract count.
