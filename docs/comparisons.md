# Comparisons

Polis Protocol is a coordination protocol, not an agent framework, runtime,
memory database, graph executor, or chat UI. Its job is to give multiple AI
tools a shared folder they can all understand: capability cards, contracts,
chronicle lines, routing stats, lessons, reviews, and amendments.

This page helps place Polis next to tools people already know.

| Tool or pattern | Primary job | Runtime required | Multi-vendor by default | Learning loop | Governance / amendments |
|---|---|---:|---:|---:|---:|
| Polis Protocol | Shared coordination protocol for AI agents | No | Yes | Yes, via settled contracts | Yes |
| AGENTS.md | Repository instructions for coding agents | No | Partly, where supported | No | No |
| CrewAI | Python framework for crews and flows | Yes | Yes, through model integrations | Application-defined | Application-defined |
| LangGraph | Stateful graph runtime for agent workflows | Yes | Yes, through model integrations | Application-defined | Application-defined |
| hcom | Terminal messaging and process coordination | Yes | Yes | No built-in routing memory | No |
| SwarmClaw | Self-hosted multi-agent runtime/dashboard | Yes | Yes | Runtime-defined | Runtime-defined |
| Agent memory systems | Long-term recall for agents | Usually | Usually | Yes, focused on memory | No |

## AGENTS.md

What it is: a plain markdown instruction file that AI coding agents can read
for repo-specific guidance. Codex and other tools can use it to understand
project conventions, commands, and constraints.

Where Polis overlaps: Polis writes `AGENTS.md` as one of its bridge pointers.
That file tells Codex where to find the canonical `_polis/CONSTITUTION.md`.

Where Polis differs: AGENTS.md is mostly instruction. Polis is shared state and
process: open contracts, settled contracts, citizens, routing history, lessons,
reviews, and amendments. A single AGENTS.md can tell an agent how to behave;
Polis lets many agents coordinate what happened, who owns what, and what the
team has learned.

Use together when: you want Codex or another AGENTS.md-aware tool to enter a
project and immediately discover the same coordination layer that Claude,
Gemini, and other agents are using.

Links: [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md), [agents.md](https://agents.md/).

## CrewAI

What it is: an open-source framework for orchestrating autonomous AI agents and
building workflows. CrewAI organizes agents into Crews and uses Flows for
structured, event-driven orchestration.

Where Polis overlaps: both care about teams of agents, role clarity, task
assignment, and workflow discipline.

Where Polis differs: CrewAI executes agent workflows in an application runtime.
Polis does not run agents. It is a markdown protocol that any tool can read and
write. CrewAI is where you build an agent app; Polis is where independent agent
tools can leave durable coordination records for each other.

Use together when: a CrewAI application needs a human-readable project ledger,
or when CrewAI agents should coordinate with external coding agents such as
Claude Code, Codex, Gemini CLI, or local agents.

Link: [CrewAI introduction](https://docs.crewai.com/introduction).

## LangGraph

What it is: a low-level orchestration framework and runtime for long-running,
stateful agent applications. LangGraph represents workflows as stateful graphs
with nodes, edges, persistence, and deployment support.

Where Polis overlaps: both make agent coordination more explicit than ad hoc
chat. Both can support multi-step, long-running work.

Where Polis differs: LangGraph defines executable control flow. Polis defines a
shared project protocol. LangGraph decides what node runs next inside an app;
Polis helps separate AI tools agree on contracts, ownership, routing evidence,
and lessons across sessions.

Use together when: a LangGraph app should publish its work into the same
project ledger that coding assistants and review agents read, or when Polis
contracts should trigger a LangGraph workflow.

Links: [LangGraph overview](https://docs.langchain.com/oss/python/langgraph), [LangGraph product page](https://www.langchain.com/langgraph).

## hcom

What it is: a tool for AI agents to message, watch, and spawn each other across
terminals. It is aimed at live coordination between running agent processes.

Where Polis overlaps: both are vendor-agnostic coordination tools for multiple
agent sessions.

Where Polis differs: hcom is a live communication/process layer. Polis is a
durable protocol layer. hcom helps agents talk right now; Polis preserves the
shared record of contracts, decisions, lessons, and routing stats that should
survive after the terminal session ends.

Use together when: you want live terminal-to-terminal agent messaging plus a
markdown ledger that remains useful across days or weeks.

Link: [hcom on PyPI](https://pypi.org/project/hcom/).

## SwarmClaw

What it is: a self-hosted AI agent runtime and multi-agent framework with agent
memory, MCP tools, schedules, delegation, provider support, and a dashboard.

Where Polis overlaps: both address multi-agent work across providers and both
care about delegation, memory, and coordination.

Where Polis differs: SwarmClaw is an operating environment for agents. Polis is
portable coordination state. SwarmClaw can host and orchestrate agents; Polis
can be copied into any repo and used by tools that only know how to read and
write markdown.

Use together when: SwarmClaw is the runtime, but the project still needs a
repo-local protocol that external tools and humans can inspect without opening
the runtime.

Link: [SwarmClaw on GitHub](https://github.com/swarmclawai/swarmclaw).

## Agent Memory Systems

What they are: tools such as Hindsight or Mem0 give agents persistent recall
across sessions. They store facts, preferences, experiences, or summaries and
retrieve relevant memories when an agent needs context.

Where Polis overlaps: Polis has a learning loop too. Settled contracts produce
lessons and update routing statistics, so the team gets better at deciding who
should do what.

Where Polis differs: memory systems optimize recall. Polis optimizes
coordination. A memory system might remember that a user prefers concise prose;
Polis records that Gemini translated a parent newsletter well, that Codex
handled frontend contracts poorly last week, or that the team ratified a new
review rule.

Use together when: agents need both personal or semantic memory and a shared
project governance layer. Memory can help each citizen reason; Polis helps the
citizens coordinate.

Links: [Hindsight](https://github.com/vectorize-io/hindsight), [Mem0 docs](https://docs.mem0.ai/).

## Rule of Thumb

Use Polis when the problem is not "how do I run an agent?" but "how do several
different agents share work, route tasks, learn from outcomes, and change their
rules without a central server?"
