import assert from "node:assert/strict";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`https://polis.test${path}`, { headers: { accept: "text/html", host: "polis.test", "x-forwarded-proto": "https" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the complete Polis landing page", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /Git-native coordination for coding agents/);
  assert.match(html, /uvx polis-protocol init/);
  assert.match(html, /A modeled learning effect—not field telemetry/);
  assert.match(html, /advisory file reservations/i);
  assert.match(html, /id="what"/);
  assert.match(html, /id="workflow"/);
  assert.match(html, /id="evidence"/);
  assert.match(html, /id="fit"/);
  assert.match(html, /id="quick-start"/);
  assert.match(html, /application\/ld\+json/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});

test("adds security and privacy response headers", async () => {
  const response = await render();
  assert.match(response.headers.get("content-security-policy") ?? "", /frame-ancestors 'none'/);
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  assert.equal(response.headers.get("x-frame-options"), "DENY");
  assert.equal(response.headers.get("referrer-policy"), "strict-origin-when-cross-origin");
  assert.match(response.headers.get("permissions-policy") ?? "", /camera=\(\)/);
});

test("renders dynamic robots and sitemap routes", async () => {
  const robots = await render("/robots.txt");
  const robotsText = await robots.text();
  assert.equal(robots.status, 200);
  assert.match(robotsText, /Allow: \//);
  assert.match(robotsText, /https:\/\/polis\.test\/sitemap\.xml/);

  const sitemap = await render("/sitemap.xml");
  const sitemapText = await sitemap.text();
  assert.equal(sitemap.status, 200);
  assert.match(sitemapText, /https:\/\/polis\.test\//);
});
