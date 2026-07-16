# Main branch security

All changes to `main` enter through squash-merged pull requests. The repository
requires a stable `Required checks` gate, current-branch validation, CodeQL
analysis, linear history, and resolved review conversations.

External contributor workflows require explicit maintainer approval before any
contributor-controlled code runs. They receive no repository secrets and no
write access to repository contents.

The solo maintainer may use an auditable pull-request-only bypass for the review
rule when self-approval is impossible. That bypass does not apply to the core
status, CodeQL, history, deletion, or force-push protections.

If a protection gate causes a lockout, disable the affected ruleset, repair the
gate in a pull request, verify the correction, and reactivate the ruleset. Do
not delete rulesets or weaken the external-contributor execution boundary as a
shortcut.
