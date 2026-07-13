# Polis Protocol website

This directory contains the production source for the public Polis Protocol website:

<https://polis-protocol.ymlsora.chatgpt.site>

The site is a single-route Vinext application deployed with OpenAI Sites. It has no authentication, persistence, analytics, cookies, CMS, or external runtime data.

## Local development

Requires Node.js 22.13 or newer.

```bash
npm ci
npm run dev
```

## Verification

```bash
npm test
npm run lint
```

The Sites project identifier is stored in `.openai/hosting.json`; it contains no secret credentials.
