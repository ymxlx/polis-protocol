# Publishing Polis to the official MCP registry

This is the one-time manual step to list `polis mcp` in
[registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io). It needs
**(a)** the PyPI package re-published at the version in [`server.json`](../server.json) and
**(b)** an interactive GitHub login, so it can't run unattended in CI.

Everything in the repo is already prepared:
- [`server.json`](../server.json) — namespace `io.github.yehudalevy-collab/polis-protocol`,
  PyPI identifier `polis-protocol`, stdio transport, `packageArguments: ["mcp"]`.
- A `polis-protocol` console-script alias (in `pyproject.toml`) so registry clients that run
  `uvx polis-protocol mcp` start the server. (`polis-protocol mcp` == `polis mcp`.)
- The ownership marker `<!-- mcp-name: io.github.yehudalevy-collab/polis-protocol -->` at the
  top of `README.md`, which PyPI ships in the package long-description for verification.

## 0. Prerequisite: publish the package version named in `server.json`

The registry validates that the PyPI package at `packages[0].version` contains the
`mcp-name:` marker. So that version must be live on PyPI first.

```bash
# from the repo root, on the merged branch
rm -rf dist && uv build
export TWINE_USERNAME=__token__ TWINE_PASSWORD='<a fresh project-scoped PyPI token>'
uvx twine upload dist/*
unset TWINE_PASSWORD
# verify the alias + marker shipped
uvx --refresh --from polis-protocol==2.0.1 polis-protocol version
```

If you bump the version again later, edit `pyproject.toml` and **both** `version` fields in
`server.json` in lockstep. `polis/__init__.py` reads `__version__` from the installed
distribution metadata (`importlib.metadata`), so it tracks `pyproject.toml` automatically —
only update its source-tree fallback constant when you start the *next* version's work.
Also: `server.json` `description` must be **≤ 100 chars** (the registry returns 422 otherwise),
and the Registry JWT expires quickly — run `mcp-publisher login github` immediately before
`mcp-publisher publish`.

## 1. Install the mcp-publisher CLI

```bash
# Homebrew (any platform)
brew install mcp-publisher
# …or download the latest release binary:
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher && sudo mv mcp-publisher /usr/local/bin/
```

## 2. Authenticate (GitHub device flow)

```bash
mcp-publisher login github
```

Opens a GitHub device-flow prompt: visit the URL, enter the code, authorize. This proves you
own the `io.github.yehudalevy-collab/*` namespace (your GitHub account is `yehudalevy-collab`).

## 3. Publish

```bash
# from the repo root, where server.json lives
mcp-publisher publish
```

The CLI validates `server.json` against the schema, confirms the PyPI package carries the
`mcp-name:` marker, and uploads. On success the server appears at
`https://registry.modelcontextprotocol.io/v0/servers?search=polis`.

## 4. Verify

```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=polis-protocol" | jq '.servers[].name'
```

End users can then add it with their MCP client, e.g.:

```bash
claude mcp add polis -- uvx polis-protocol mcp
```

## Updating later

Re-publishing a new version is the same flow: bump the three version fields, publish the
package to PyPI, then `mcp-publisher publish` again (the GitHub login is cached).
