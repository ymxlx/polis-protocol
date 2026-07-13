import { CopyButton } from "./CopyButton";
import { HashNavigator } from "./HashNavigator";

const repository = "https://github.com/yehudalevy-collab/polis-protocol";

const concepts = [
  {
    index: "01",
    title: "Agent profiles",
    detail: "Capability cards describe each agent’s strengths, cost, and availability.",
    path: "citizens/*/capability_card.yml",
  },
  {
    index: "02",
    title: "Structured tasks",
    detail: "Contracts keep intent, ownership, acceptance criteria, and settlement together.",
    path: "contracts/open/*.md",
  },
  {
    index: "03",
    title: "Shared record",
    detail: "An append-only chronicle gives every vendor the same project history.",
    path: "chronicle.md",
  },
  {
    index: "04",
    title: "Lessons + rules",
    detail: "Tagged lessons inform future routing; amendments evolve the protocol itself.",
    path: "lessons/ · amendments/",
  },
];

const workflow = [
  ["01", "Initialize", "Create the shared _polis/ workspace and agent bridge files."],
  ["02", "Open", "Record a task with acceptance criteria, capability tags, and stakes."],
  ["03", "Recommend", "Compare capability cards and prior outcomes; explain the routing score."],
  ["04", "Claim", "Assign an owner and optionally publish advisory file reservations."],
  ["05", "Complete", "Settle the contract with outcome, quality, time, and evidence."],
  ["06", "Carry forward", "Load matching lessons and guardrails into the next relevant task."],
];

const quickStart = [
  {
    step: "01",
    command: "uvx polis-protocol init",
    title: "Create the workspace",
    detail: "Adds _polis/, bridge instructions, and your first agent profile without a hosted service.",
  },
  {
    step: "02",
    command: "polis status",
    title: "Inspect shared state",
    detail: "Shows citizens, active contracts, reservations, lessons, and protocol health.",
  },
  {
    step: "03",
    command: "polis contract open --help",
    title: "Open the first task",
    detail: "Review the exact flags for title, capability tags, stakes, and the opening agent.",
  },
];

function BrandMark({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <g fill="none" stroke="currentColor" strokeWidth="1" strokeLinejoin="round">
        <polygon points="12,3.5 19.4,7.75 19.4,16.25 12,20.5 4.6,16.25 4.6,7.75" />
        <path d="M12 12 12 3.5M12 12 19.4 7.75M12 12 19.4 16.25M12 12 12 20.5M12 12 4.6 16.25M12 12 4.6 7.75" />
      </g>
      <g fill="currentColor">
        <circle cx="12" cy="3.5" r="1.4" />
        <circle cx="19.4" cy="7.75" r="1.4" />
        <circle cx="19.4" cy="16.25" r="1.4" />
        <circle cx="12" cy="20.5" r="1.4" />
        <circle cx="4.6" cy="16.25" r="1.4" />
        <circle cx="4.6" cy="7.75" r="1.4" />
      </g>
      <circle cx="12" cy="12" r="2.2" fill="var(--cyan)" />
    </svg>
  );
}

function SectionHeading({
  index,
  eyebrow,
  title,
  detail,
}: {
  index: string;
  eyebrow: string;
  title: string;
  detail: string;
}) {
  return (
    <div className="section-heading">
      <div className="section-index" aria-hidden="true">
        <span>[ {index} ]</span>
        <span>{eyebrow}</span>
      </div>
      <div>
        <h2>{title}</h2>
        <p>{detail}</p>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <>
      <HashNavigator />
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>

      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="#top" aria-label="Polis Protocol home">
            <span className="brand-mark">
              <BrandMark />
            </span>
            <span>POLIS</span>
            <span className="brand-meta">{"// PROTOCOL · V2.0"}</span>
          </a>

          <nav className="primary-nav" aria-label="Primary navigation">
            <a href="#what">What it creates</a>
            <a href="#workflow">Workflow</a>
            <a href="#evidence">Evidence</a>
            <a href="#fit">Fit</a>
          </nav>

          <a className="header-cta" href="#quick-start">
            Quick start <span aria-hidden="true">↓</span>
          </a>
        </div>
      </header>

      <main id="main-content">
        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="page-shell hero-grid">
            <div className="hero-copy">
              <p className="eyebrow">[ LOCAL-FIRST · MARKDOWN · GIT ]</p>
              <h1 id="hero-title">Git-native coordination for coding agents.</h1>
              <p className="hero-lede">
                Polis gives Claude Code, Codex, Gemini, Cursor, and other tools one shared
                <code> _polis/</code> folder for tasks, owners, routing history, lessons,
                and decisions—without a hosted runtime or proprietary database.
              </p>

              <div className="hero-actions">
                <a className="primary-action" href="#quick-start">
                  View quick start <span aria-hidden="true">↓</span>
                </a>
                <a className="secondary-action" href={repository} target="_blank" rel="noopener">
                  View source <span aria-hidden="true">↗</span>
                </a>
              </div>

              <div className="command-line command-line-hero">
                <span className="prompt" aria-hidden="true">$</span>
                <code>uvx polis-protocol init</code>
                <CopyButton command="uvx polis-protocol init" label="Copy install command" />
              </div>
              <p className="command-note">One command. No server. No database. Plain files in your repo.</p>
            </div>

            <div className="coordination-map" aria-label="Three coding agents coordinating through one shared Polis workspace">
              <div className="map-label">
                <span className="signal-dot" aria-hidden="true" />
                SHARED PROJECT STATE
              </div>
              <div className="agent-node node-claude">
                <span>AGENT / 01</span>
                <strong>CLAUDE</strong>
                <small>RESEARCH</small>
              </div>
              <div className="agent-node node-codex">
                <span>AGENT / 02</span>
                <strong>CODEX</strong>
                <small>IMPLEMENTATION</small>
              </div>
              <div className="agent-node node-gemini">
                <span>AGENT / 03</span>
                <strong>GEMINI</strong>
                <small>REVIEW</small>
              </div>
              <div className="map-line map-line-a" aria-hidden="true" />
              <div className="map-line map-line-b" aria-hidden="true" />
              <div className="map-line map-line-c" aria-hidden="true" />
              <div className="polis-node">
                <span className="polis-node-mark"><BrandMark size={30} /></span>
                <span>ONE SHARED WORKSPACE</span>
                <strong>_polis/</strong>
                <small>TRACKED IN GIT</small>
              </div>
              <div className="map-status">
                <span>03 ACTIVE CITIZENS</span>
                <span>01 OPEN CONTRACT</span>
                <span>12 LESSONS AVAILABLE</span>
              </div>
            </div>
          </div>
        </section>

        <section className="content-section" id="what" aria-labelledby="what-title">
          <div className="page-shell">
            <SectionHeading
              index="01"
              eyebrow="WHAT INIT CREATES"
              title="One folder every agent can understand."
              detail="The protocol owns only _polis/. Your project stays yours; the coordination record stays portable, reviewable, and diffable."
            />

            <div className="what-grid">
              <div className="folder-tree" aria-label="Example Polis workspace folder structure">
                <div className="folder-toolbar">
                  <span>WORKSPACE / _POLIS</span>
                  <span>GIT STATUS: CLEAN</span>
                </div>
                <pre><code>{`_polis/
├── CONSTITUTION.md
├── index.md
├── chronicle.md
├── citizens/
│   └── <agent-id>/
│       ├── capability_card.yml
│       ├── status.md
│       └── inbox.md
├── contracts/
│   ├── open/
│   └── settled/
├── lessons/
└── amendments/`}</code></pre>
              </div>

              <div className="concept-list">
                {concepts.map((concept) => (
                  <article className="concept-item" key={concept.index}>
                    <span className="concept-index">{concept.index}</span>
                    <div>
                      <h3>{concept.title}</h3>
                      <p>{concept.detail}</p>
                      <code>{concept.path}</code>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="content-section section-alt" id="workflow" aria-labelledby="workflow-title">
          <div className="page-shell">
            <SectionHeading
              index="02"
              eyebrow="OPERATING SEQUENCE"
              title="Work moves through a visible loop."
              detail="Routing is explainable, ownership is explicit after a claim, and completed work leaves evidence the next agent can use."
            />

            <ol className="workflow-grid">
              {workflow.map(([index, title, detail]) => (
                <li key={index}>
                  <span className="workflow-index">SEQ.{index}</span>
                  <h3>{title}</h3>
                  <p>{detail}</p>
                </li>
              ))}
            </ol>

            <div className="boundary-grid" aria-labelledby="boundary-title">
              <div className="boundary-intro">
                <p className="eyebrow">[ OPERATING BOUNDARY ]</p>
                <h3 id="boundary-title">Coordination, not execution.</h3>
                <p>Polis makes shared intent and history explicit. It does not become a scheduler, sandbox, or security boundary.</p>
              </div>
              <div className="boundary-column boundary-yes">
                <h4><span aria-hidden="true">+</span> What Polis coordinates</h4>
                <ul>
                  <li>Structured tasks and claimed ownership</li>
                  <li>Explainable routing recommendations</li>
                  <li>Shared outcomes, lessons, and decisions</li>
                  <li>Advisory overlapping-path warnings</li>
                </ul>
              </div>
              <div className="boundary-column boundary-no">
                <h4><span aria-hidden="true">−</span> What Polis does not enforce</h4>
                <ul>
                  <li>Agent execution or process scheduling</li>
                  <li>Filesystem locks or race prevention</li>
                  <li>Security isolation or permissions</li>
                  <li>Compliance by agents outside the workflow</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="content-section evidence-section" id="evidence" aria-labelledby="evidence-title">
          <div className="page-shell">
            <SectionHeading
              index="03"
              eyebrow="REPRODUCIBLE SIMULATION"
              title="A modeled learning effect—not field telemetry."
              detail="The bundled benchmark makes its assumptions inspectable and its result reproducible from the command line."
            />

            <div className="evidence-grid">
              <figure className="simulation-figure">
                <div className="figure-head">
                  <span>180 SYNTHETIC TASKS · 14 FAILURE MODES · SEED 0</span>
                  <strong>MODE: LEARNING</strong>
                </div>
                <div className="bar-chart" aria-hidden="true">
                  <div className="bar-row">
                    <div className="bar-label"><span>MEMORYLESS SETUP</span><strong>65%</strong></div>
                    <div className="bar-track"><span className="bar bar-memoryless" /></div>
                  </div>
                  <div className="bar-row">
                    <div className="bar-label"><span>POLIS MODEL</span><strong>7%</strong></div>
                    <div className="bar-track"><span className="bar bar-polis" /></div>
                  </div>
                </div>
                <div className="modeled-result">
                  <strong>−89%</strong>
                  <span>MODELED REPEAT-ERROR RATE</span>
                </div>
                <figcaption>
                  In this simulation, a recorded failure becomes a standing check after its first occurrence. The result demonstrates the designed memory loop; it is not customer telemetry or a real-world error-rate guarantee.
                </figcaption>
              </figure>

              <aside className="method-panel" aria-label="Benchmark method and limitations">
                <p className="eyebrow">[ READ THE METHOD ]</p>
                <h3>Evidence with its boundary attached.</h3>
                <dl>
                  <div><dt>Compares</dt><dd>A setup with no persistent shared lessons against the Polis learning model.</dd></div>
                  <div><dt>Demonstrates</dt><dd>How recorded failure classes can become reusable checks in later matching tasks.</dd></div>
                  <div><dt>Does not prove</dt><dd>Production reliability, universal compliance, or collision-free concurrent editing.</dd></div>
                </dl>
                <div className="method-actions">
                  <a href={`${repository}/blob/main/polis/bench.py`} target="_blank" rel="noopener">Inspect benchmark source <span aria-hidden="true">↗</span></a>
                  <div className="mini-command"><code>polis bench --mode learning</code><CopyButton command="polis bench --mode learning" label="Copy benchmark command" /></div>
                </div>
              </aside>
            </div>

            <details className="evidence-table">
              <summary>View benchmark values as a table</summary>
              <table>
                <caption>Repeat-error simulation results</caption>
                <thead><tr><th scope="col">Setup</th><th scope="col">Tasks</th><th scope="col">Failure modes</th><th scope="col">Repeat-error rate</th></tr></thead>
                <tbody>
                  <tr><th scope="row">No persistent shared lessons</th><td>180</td><td>14</td><td>65%</td></tr>
                  <tr><th scope="row">Polis learning model</th><td>180</td><td>14</td><td>7%</td></tr>
                </tbody>
              </table>
            </details>
          </div>
        </section>

        <section className="content-section section-alt" id="fit" aria-labelledby="fit-title">
          <div className="page-shell">
            <SectionHeading
              index="04"
              eyebrow="WHEN TO USE POLIS"
              title="Use the protocol when routing and memory matter."
              detail="The strongest fit is a real repository shared by multiple coding agents—not every AI workflow."
            />

            <div className="fit-grid">
              <article className="fit-card fit-use">
                <h3><span aria-hidden="true">+</span> Reach for Polis when</h3>
                <ul>
                  <li>Two or more coding agents touch the same repository.</li>
                  <li>You switch vendors and prior decisions get lost.</li>
                  <li>Task ownership and routing quality need an audit trail.</li>
                  <li>Lessons should influence future matching tasks.</li>
                </ul>
              </article>
              <article className="fit-card fit-skip">
                <h3><span aria-hidden="true">−</span> Skip it when</h3>
                <ul>
                  <li>One well-prompted agent already handles the work.</li>
                  <li>You only need shared notes, not ownership or learned routing.</li>
                  <li>You need an execution runtime, scheduler, or security boundary.</li>
                  <li>Your agents will not maintain the shared records consistently.</li>
                </ul>
              </article>
            </div>
          </div>
        </section>

        <section className="quick-start" id="quick-start" aria-labelledby="quick-start-title">
          <div className="page-shell">
            <div className="quick-start-head">
              <div>
                <p className="eyebrow">[ 05 · QUICK START ]</p>
                <h2 id="quick-start-title">Start with one command.</h2>
              </div>
              <p>Python 3.10+ · MIT licensed · files stay in your repository</p>
            </div>

            <ol className="quick-start-list">
              {quickStart.map((item) => (
                <li key={item.step}>
                  <div className="quick-step"><span>{item.step}</span><h3>{item.title}</h3></div>
                  <p>{item.detail}</p>
                  <div className="command-line">
                    <span className="prompt" aria-hidden="true">$</span>
                    <code>{item.command}</code>
                    <CopyButton command={item.command} label={`Copy command: ${item.command}`} />
                  </div>
                </li>
              ))}
            </ol>

            <div className="trust-links">
              <a href={repository} target="_blank" rel="noopener">Source <span aria-hidden="true">↗</span></a>
              <a href={`${repository}#quick-start`} target="_blank" rel="noopener">Documentation <span aria-hidden="true">↗</span></a>
              <a href={`${repository}/blob/main/scripts/demo.sh`} target="_blank" rel="noopener">Demo <span aria-hidden="true">↗</span></a>
              <a href="https://pypi.org/project/polis-protocol/" target="_blank" rel="noopener">PyPI <span aria-hidden="true">↗</span></a>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="page-shell footer-inner">
          <div className="footer-brand"><BrandMark size={20} /><strong>POLIS PROTOCOL</strong><span>V2.0 · STABLE · MIT</span></div>
          <nav aria-label="Project links">
            <a href={`${repository}/actions`} target="_blank" rel="noopener">Tests</a>
            <a href={`${repository}/releases`} target="_blank" rel="noopener">Releases</a>
            <a href={`${repository}/blob/main/LICENSE`} target="_blank" rel="noopener">License</a>
            <a href={`${repository}/blob/main/SECURITY.md`} target="_blank" rel="noopener">Security</a>
            <a href="https://open-vsx.org/extension/yehudalevy-collab/polis-protocol" target="_blank" rel="noopener">Open VSX</a>
          </nav>
        </div>
      </footer>

    </>
  );
}
