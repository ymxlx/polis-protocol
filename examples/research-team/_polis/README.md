# Polis Coordination Folder — Pesaj 2027 Educational Materials

This folder is the coordination layer for the three AI agents working on Pesaj 2027.

## What is in here

- `CONSTITUTION.md` — canonical protocol every citizen follows.
- `index.md` — "where things stand" page.
- `chronicle.md` — append-only log of meaningful events.
- `citizens/` — one folder per citizen: capability card, status, inbox, journal.
- `contracts/open/` — currently active tasks.
- `contracts/settled/` — closed tasks with retrospectives and lessons.
- `contracts/routing_stats.yml` — what the bandit knows about who's good at what.
- `lessons/` — retrospective notes, filed by capability tag.
- `reviews/` — chavruta review notes for high-stakes contracts.
- `amendments/ratified/` — accepted changes to the protocol itself.

## Read order if you're new

1. `index.md`
2. `chronicle.md` (the last 20 lines tell the recent story)
3. Any contract or lesson the chronicle links to
4. `contracts/routing_stats.yml` to see what the router knows
