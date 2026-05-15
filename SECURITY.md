# Security Policy

## Reporting a vulnerability

Polis Protocol is a markdown specification plus two Python scripts (`init_polis.py`, `route_contract.py`) that operate on local files only. There is no network code, no server, and no privileged execution path. That said, file-system tools can still have surprising failure modes.

If you find one of the following, please report it privately first:

- **Path traversal** — e.g. an agent-id or contract-id that escapes `_polis/` and writes elsewhere.
- **YAML deserialization issues** — e.g. a capability card or contract that abuses `yaml.safe_load` (we only ever use the safe loader, but report regressions).
- **Signature spoofing** — the card signature is an integrity check, not a security boundary, but exploits that defeat the intended integrity property are still useful to know.
- **Anything that lets an untrusted file at one path cause writes at an unexpected path** when running the bundled scripts.

Send a private report to **yehuda.moshe24@gmail.com** with:

- The polis layout that triggers the issue (a minimal `.tar.gz` is ideal).
- The exact command you ran.
- Observed vs. expected behavior.

You'll get an acknowledgement within 72 hours and a fix or mitigation plan within 14 days. Public disclosure is welcome 30 days after the fix lands, or sooner by mutual agreement.

## What is *not* in scope

- **Adversarial agents.** Polis trusts the citizens you register. If a registered agent files a malicious lesson or routes contracts dishonestly, that is a governance problem, not a security one — handle it via the amendment process and the chronicle.
- **LLM prompt injection.** Polis files can be read by LLMs; an attacker who can write to your `_polis/` folder can influence agent behavior. The mitigation is the same as for any markdown documentation: review changes before letting an agent act on them.
- **External LLM API security.** That's the vendor's job, not Polis's.

Polis aims to be hard to misuse, not impervious to a hostile operator.
