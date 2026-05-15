---
name: Bug report
about: Something in the scripts or templates doesn't behave the way the docs say it should.
title: '[bug] '
labels: bug
assignees: ''
---

## What happened

<!-- One paragraph. What did you run, what did you expect, what did you see instead? -->

## Minimal reproduction

<!-- The fewer files the better. A 3-file polis is more useful than a 30-file one. -->

```
$ python3 scripts/init_polis.py --project-root ... --agent-id ...
$ python3 scripts/route_contract.py --polis-root ... --contract ...
```

## Polis layout

<!-- Output of `find _polis -type f | sort` (truncate if huge). -->

```
_polis/
├── ...
```

## Environment

- OS:
- Python version (`python3 --version`):
- PyYAML version (`python3 -c "import yaml; print(yaml.__version__)"`):
- Polis commit / tag:

## Notes

<!-- Workarounds you tried, suspected root cause, anything else. -->
