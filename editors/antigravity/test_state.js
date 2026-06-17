// Unit tests for the Polis extension's pure state helpers.  Run: node test_state.js
// (Node-only; the repo's Python CI runs this via a dedicated step.)
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const state = require("./state");

const sample = JSON.parse(fs.readFileSync(path.join(__dirname, "sample_state.json"), "utf8"));

// contractRows: one row per open contract, owner + tags surfaced from the API.
const rows = state.contractRows(sample);
assert.strictEqual(rows.length, sample.open.length, "one row per open contract");
const wired = rows.find((r) => r.id === "wire-the-api");
assert.ok(wired, "expected the sample contract");
assert.strictEqual(wired.owner, "claude-dev-acme", "owner surfaced from API");
assert.ok(wired.description.includes("@claude-dev-acme"), "owner shown in description");
assert.ok(wired.description.includes("dev"), "required tag shown in description");

// citizenRows: one row per citizen in the dict, vendor surfaced.
const cz = state.citizenRows(sample);
assert.strictEqual(cz.length, Object.keys(sample.citizens).length, "one row per citizen");
assert.ok(cz.every((c) => typeof c.id === "string" && c.id.length), "every citizen has an id");
assert.ok(cz.find((c) => c.id === "claude-dev-acme").description.includes("anthropic"), "vendor shown");

// openCount mirrors the open list.
assert.strictEqual(state.openCount(sample), sample.open.length, "openCount matches");

// Garbage / empty input must never throw (the extension falls back to files).
assert.deepStrictEqual(state.contractRows(null), [], "null state -> []");
assert.deepStrictEqual(state.citizenRows(undefined), [], "undefined state -> []");
assert.strictEqual(state.openCount({}), 0, "empty state -> 0");

// fetchState resolves null (not throw) when nothing is listening — the fallback trigger.
state.fetchState("http://127.0.0.1:9", 300).then((s) => {
  assert.strictEqual(s, null, "unreachable server -> null");
  console.log("ok - all extension state helper tests passed");
}).catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
