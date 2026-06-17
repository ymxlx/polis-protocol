// Shared state access for the Polis extension.
//
// Prefer the `polis serve` control-plane API (GET /api/state) so the extension is
// a *thin client* of the same data the CLI and MCP server expose — no duplicated
// parsing/scoring logic. When no server is running, the extension falls back to
// listing _polis/ files directly (see extension.js).
//
// These helpers are pure (no `vscode` import) so they can be unit-tested with node.
const http = require("http");

const DEFAULT_URL = "http://127.0.0.1:7341";

/** GET <base>/api/state. Resolves the parsed object, or null if unreachable/non-200/bad JSON. */
function fetchState(base, timeoutMs = 600) {
  return new Promise((resolve) => {
    let url;
    try {
      url = new URL("/api/state", base || DEFAULT_URL);
    } catch (_) {
      resolve(null);
      return;
    }
    const req = http.get(url, (res) => {
      if (res.statusCode !== 200) {
        res.resume();
        resolve(null);
        return;
      }
      let body = "";
      res.setEncoding("utf8");
      res.on("data", (d) => { body += d; });
      res.on("end", () => {
        try { resolve(JSON.parse(body)); } catch (_) { resolve(null); }
      });
    });
    req.on("error", () => resolve(null));
    req.setTimeout(timeoutMs, () => { req.destroy(); resolve(null); });
  });
}

/** Open contracts as display rows: {id, owner, routed, label, description}. Pure. */
function contractRows(state) {
  const open = (state && state.open) || [];
  return open.map((c) => ({
    id: c.contract_id,
    owner: c.owner || null,
    routed: (c.routing && c.routing.recommended_by_router) || null,
    label: c.contract_id,
    description: [
      c.owner ? `@${c.owner}` : "unclaimed",
      (c.required_tags || []).join(","),
    ].filter(Boolean).join(" · "),
  }));
}

/** Citizen rows from the citizens dict: {id, label, description}. Pure. */
function citizenRows(state) {
  const cz = (state && state.citizens) || {};
  return Object.keys(cz).map((id) => {
    const c = cz[id] || {};
    return {
      id,
      label: id,
      description: [c.vendor, (c.tags || []).join(",")].filter(Boolean).join(" · "),
    };
  });
}

/** Number of open contracts (for the status bar). Pure. */
function openCount(state) {
  return ((state && state.open) || []).length;
}

module.exports = { DEFAULT_URL, fetchState, contractRows, citizenRows, openCount };
