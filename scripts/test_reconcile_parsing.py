#!/usr/bin/env python3
"""
Regression tests for the reconcile body parsers in route_contract.py.

These guard against the class of bug where re.search would match the FIRST
occurrence of `actual_minutes` anywhere in the body (including prose mentions
in the Plan paragraph) and capture whatever digit was nearby — instead of
the labeled `actual_minutes: <N>` line in the Settlement section.

Run directly:
    python3 scripts/test_reconcile_parsing.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Importing route_contract requires PyYAML; the parsers themselves don't.
# Import the functions lazily so we can give a friendly error if yaml is missing.
try:
    from route_contract import _extract_quality, _extract_actual_minutes
except ImportError as e:
    print(f"Import failed: {e}\nInstall PyYAML: pip install pyyaml")
    sys.exit(1)


def check(name: str, got, want) -> bool:
    ok = got == want
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] {name}: got={got!r} want={want!r}")
    return ok


def main() -> int:
    failures = 0

    # --- actual_minutes ---

    # The original failure: prose mention of "actual_minutes per paper × 12
    # papers" appears before the labeled line. The old regex captured 12. The
    # fix should anchor on start-of-line + colon and return 72.
    body_prose_before_label = """
## Assignment

### Plan
Roughly 6 actual_minutes per paper × 12 papers = ~72 actual minutes total.

## Settlement

### Outcome
Done.

actual_minutes: 72
"""
    if not check("actual_minutes ignores prose mention", _extract_actual_minutes({}, body_prose_before_label), 72):
        failures += 1

    # Variant: labeled line after a markdown heading marker.
    body_heading_label = """
### actual_minutes: 90
"""
    if not check("actual_minutes after heading marker", _extract_actual_minutes({}, body_heading_label), 90):
        failures += 1

    # Variant: list-item label.
    body_list_label = """
- actual_minutes: 15
"""
    if not check("actual_minutes after list marker", _extract_actual_minutes({}, body_list_label), 15):
        failures += 1

    # Variant: space form `actual minutes: N`.
    body_space_form = """
actual minutes: 42
"""
    if not check("actual minutes (space form)", _extract_actual_minutes({}, body_space_form), 42):
        failures += 1

    # Frontmatter wins over body.
    if not check(
        "actual_minutes frontmatter overrides body",
        _extract_actual_minutes({"actual_minutes": 5}, "actual_minutes: 999"),
        5,
    ):
        failures += 1

    # No label, no frontmatter → default 30.
    if not check(
        "actual_minutes default when absent",
        _extract_actual_minutes({}, "## Settlement\nNo timing recorded."),
        30,
    ):
        failures += 1

    # Prose only, no labeled line → default 30 (no false capture).
    if not check(
        "actual_minutes prose-only does not false-match",
        _extract_actual_minutes({}, "Took roughly 6 actual_minutes per paper × 12 papers."),
        30,
    ):
        failures += 1

    # --- quality self-score ---

    # `Quality self-score: 5` on a single line.
    body_inline_quality = """
### Settlement

Quality self-score: 5
"""
    if not check("quality inline form", _extract_quality({}, body_inline_quality), 5):
        failures += 1

    # Heading + blank line + number-on-its-own-line (historical layout).
    body_heading_quality = """
### Quality self-score

4

### Notes
"""
    if not check("quality heading-then-number form", _extract_quality({}, body_heading_quality), 4):
        failures += 1

    # Frontmatter wins.
    if not check(
        "quality frontmatter overrides body",
        _extract_quality({"quality_score": 2}, "Quality self-score: 5"),
        2,
    ):
        failures += 1

    # Out-of-range frontmatter is clamped to 1..5.
    if not check("quality frontmatter clamped high", _extract_quality({"quality_score": 9}, ""), 5):
        failures += 1
    if not check("quality frontmatter clamped low", _extract_quality({"quality_score": 0}, ""), 1):
        failures += 1

    # Prose mention of "5/5 in usability" does NOT false-match.
    if not check(
        "quality prose-only does not false-match",
        _extract_quality({}, "The owner scored 5/5 in usability tests."),
        3,
    ):
        failures += 1

    print()
    if failures:
        print(f"{failures} test(s) FAILED.")
        return 1
    print("All tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
