# Changelog

## 0.2.2

- The Open Contracts and Citizens views are now thin clients of `polis serve`: when a dashboard is running they show live state (owners, capability tags, routing) from its `/api/state`, falling back to reading `_polis/` files when no server is up. New `polis.serveUrl` setting.
- The status bar shows a broadcast icon when connected to a live `polis serve`.
- Fixed the Citizens view, which previously always showed empty (it listed `.md` files in `_polis/citizens/`, but citizens are directories).

## 0.2.1

- Listing now links to the project website ([polis-protocol.vercel.app](https://polis-protocol.vercel.app)) as the marketplace homepage.

## 0.2.0

- Polis 2.0: the extension now bundles the full v2 `polis` package — lessons that actually influence routing (named in `--explain`), content-hash card integrity, non-destructive init with `--repair`, reversible `polis migrate`, schema v2 + `polis doctor`, file reservations, guardrails, context packets, and Polis Bench.
- Bundled `SKILL.md` updated to the v2 control-plane workflow (always-latest install via `uvx polis-protocol`).
- Init/route commands run the bundled v2 package directly; works offline with no repo checkout.

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
