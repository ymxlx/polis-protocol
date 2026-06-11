# Polis Protocol Entry Point

This project uses the Polis Protocol for coordination between AI agents from different vendors.

**Before doing anything else, read:**

```
_polis/CONSTITUTION.md
```

The constitution describes:

- How to register as a citizen (publish a capability card).
- The four institutions: Register, Contract, Chronicle, Amendment.
- How the bandit router assigns contracts to whoever is best at the required tags.
- How lessons feed back into routing so the team gets better over time.
- How chavruta review works for high-stakes contracts.
- How to propose amendments to the protocol itself.

If you do not yet have a folder under `_polis/citizens/<your-id>/`, follow the "Registering as a citizen" section before touching any project file.

If `_polis/` does not exist at all in this project, run the bootstrap script from the polis-protocol skill:

```
python <skill-path>/scripts/init_polis.py --project-root . --agent-id <yours>
```

or scaffold by hand using the templates referenced in the constitution.

Your agent ID should follow the format `<vendor-or-tool>-<role>-<project>`. For example: `claude-research-pesaj`, `codex-frontend-pesaj`, `gemini-translator-pesaj`. Lowercase, hyphens only, 8 to 40 characters.

Welcome to the polis.
