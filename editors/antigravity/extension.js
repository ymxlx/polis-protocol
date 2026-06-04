// Polis Protocol — Antigravity / VS Code extension
// Plain CommonJS, no build step. Bundles the Polis CLI scripts in ./media.
const vscode = require("vscode");
const cp = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

let output;

function log(line) {
  if (!output) output = vscode.window.createOutputChannel("Polis Protocol");
  output.appendLine(line);
}

function mediaPath(context, file) {
  return path.join(context.extensionPath, "media", file);
}

/** First workspace folder, or undefined. */
function workspaceRoot() {
  const f = vscode.workspace.workspaceFolders;
  return f && f.length ? f[0].uri.fsPath : undefined;
}

/** Workspace folder that already contains a polis, else the first folder. */
function polisRoot() {
  const folders = vscode.workspace.workspaceFolders || [];
  for (const folder of folders) {
    if (fs.existsSync(path.join(folder.uri.fsPath, "_polis", "CONSTITUTION.md"))) {
      return folder.uri.fsPath;
    }
  }
  return workspaceRoot();
}

function hasPolis(root) {
  return !!root && fs.existsSync(path.join(root, "_polis", "CONSTITUTION.md"));
}

/** Run a bundled python script, streaming output. Resolves {code, stdout}. */
function runPython(context, script, args, cwd) {
  return new Promise((resolve) => {
    const scriptPath = mediaPath(context, script);
    log(`\n$ python3 ${script} ${args.join(" ")}`);
    let proc;
    try {
      proc = cp.spawn("python3", [scriptPath, ...args], { cwd });
    } catch (e) {
      log(`Failed to start python3: ${e.message}`);
      resolve({ code: -1, stdout: "" });
      return;
    }
    let stdout = "";
    proc.stdout.on("data", (d) => { stdout += d.toString(); log(d.toString().replace(/\n$/, "")); });
    proc.stderr.on("data", (d) => log(d.toString().replace(/\n$/, "")));
    proc.on("error", (e) => {
      if (e.code === "ENOENT") {
        vscode.window.showErrorMessage("Polis: python3 not found on PATH. Install Python 3 to use this command.");
      } else {
        vscode.window.showErrorMessage(`Polis: ${e.message}`);
      }
      resolve({ code: -1, stdout });
    });
    proc.on("close", (code) => resolve({ code, stdout }));
  });
}

/** Copy the bundled SKILL.md into a target skills dir. Returns the written path. */
function installSkillTo(context, targetDir) {
  const dest = path.join(targetDir, "polis-protocol");
  fs.mkdirSync(dest, { recursive: true });
  fs.copyFileSync(mediaPath(context, "SKILL.md"), path.join(dest, "SKILL.md"));
  return path.join(dest, "SKILL.md");
}

// ───────────────────────── commands ─────────────────────────

async function cmdInit(context) {
  const root = workspaceRoot();
  if (!root) {
    vscode.window.showErrorMessage("Polis: open a folder first, then found a polis in it.");
    return;
  }
  if (hasPolis(root)) {
    const pick = await vscode.window.showWarningMessage(
      "This workspace already has a _polis/. Re-run init anyway?", "Re-run", "Cancel");
    if (pick !== "Re-run") return;
  }
  const def = `gemini-antigravity-${path.basename(root).replace(/[^a-z0-9-]/gi, "-").toLowerCase()}`;
  const agentId = await vscode.window.showInputBox({
    prompt: "Citizen ID for this Antigravity agent",
    value: def,
  });
  if (!agentId) return;
  output && output.show(true);
  const res = await runPython(context, "init_polis.py", [
    "--project-root", root,
    "--agent-id", agentId,
    "--vendor", "google", "--model", "gemini-3", "--tool", "antigravity",
    "--no-antigravity-skill", // avoid the legacy .antigravity/skills dead path; we install correctly below
  ], root);
  if (res.code === 0) {
    // Install the skill into the path Antigravity actually reads (.agents/skills).
    try { installSkillTo(context, path.join(root, ".agents", "skills")); } catch (e) { log("skill copy: " + e.message); }
    vscode.window.showInformationMessage("Polis founded ✅  _polis/ created and the skill is in .agents/skills/.");
    vscode.commands.executeCommand("polis.refresh");
  } else {
    vscode.window.showErrorMessage("Polis: init failed — see the Polis Protocol output channel.");
  }
}

async function cmdInstallSkillGlobally(context) {
  const target = path.join(os.homedir(), ".gemini", "antigravity", "skills");
  try {
    const written = installSkillTo(context, target);
    vscode.window.showInformationMessage(
      `Polis skill installed globally for Antigravity ✅  (${written.replace(os.homedir(), "~")})`);
    log(`Installed global skill → ${written}`);
  } catch (e) {
    vscode.window.showErrorMessage(`Polis: could not install global skill — ${e.message}`);
  }
}

async function cmdInstallSkillWorkspace(context) {
  const root = workspaceRoot();
  if (!root) { vscode.window.showErrorMessage("Polis: open a folder first."); return; }
  try {
    const written = installSkillTo(context, path.join(root, ".agents", "skills"));
    vscode.window.showInformationMessage(`Polis skill installed in this workspace ✅  (.agents/skills/polis-protocol/)`);
    log(`Installed workspace skill → ${written}`);
  } catch (e) {
    vscode.window.showErrorMessage(`Polis: could not install workspace skill — ${e.message}`);
  }
}

async function cmdRoute(context) {
  const root = polisRoot();
  if (!hasPolis(root)) {
    vscode.window.showErrorMessage("Polis: no _polis/ found. Found a polis first (Polis: Found a polis).");
    return;
  }
  const openDir = path.join(root, "_polis", "contracts", "open");
  let files = [];
  try { files = fs.readdirSync(openDir).filter((f) => f.endsWith(".md")); } catch (_) { /* none */ }
  if (!files.length) {
    vscode.window.showInformationMessage("Polis: no open contracts in _polis/contracts/open/.");
    return;
  }
  const pick = await vscode.window.showQuickPick(files, { placeHolder: "Which contract should the router explain?" });
  if (!pick) return;
  output && output.show(true);
  await runPython(context, "route_contract.py", [
    "--polis-root", path.join(root, "_polis"),
    "--contract", path.join(openDir, pick),
    "--explain",
  ], root);
}

async function cmdOpenConstitution() {
  const root = polisRoot();
  const file = path.join(root || "", "_polis", "CONSTITUTION.md");
  if (!fs.existsSync(file)) {
    vscode.window.showErrorMessage("Polis: no _polis/CONSTITUTION.md in this workspace.");
    return;
  }
  const doc = await vscode.workspace.openTextDocument(file);
  vscode.window.showTextDocument(doc);
}

// ───────────────────────── tree views ─────────────────────────

class DirProvider {
  constructor(subdir, emptyLabel) { this.subdir = subdir; this.emptyLabel = emptyLabel; this._e = new vscode.EventEmitter(); this.onDidChangeTreeData = this._e.event; }
  refresh() { this._e.fire(); }
  getTreeItem(i) { return i; }
  getChildren() {
    const root = polisRoot();
    const dir = root ? path.join(root, "_polis", this.subdir) : null;
    let files = [];
    try { files = fs.readdirSync(dir).filter((f) => f.endsWith(".md")); } catch (_) { /* */ }
    if (!files.length) {
      const empty = new vscode.TreeItem(this.emptyLabel, vscode.TreeItemCollapsibleState.None);
      empty.contextValue = "empty";
      return [empty];
    }
    return files.map((f) => {
      const it = new vscode.TreeItem(f.replace(/\.md$/, ""), vscode.TreeItemCollapsibleState.None);
      const full = path.join(dir, f);
      it.command = { command: "vscode.open", title: "Open", arguments: [vscode.Uri.file(full)] };
      it.resourceUri = vscode.Uri.file(full);
      return it;
    });
  }
}

class ActionsProvider {
  getTreeItem(i) { return i; }
  getChildren() {
    const mk = (label, command, icon) => {
      const it = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
      it.command = { command, title: label };
      it.iconPath = new vscode.ThemeIcon(icon);
      return it;
    };
    return [
      mk("Found a polis", "polis.init", "rocket"),
      mk("Install skill into Antigravity (global)", "polis.installSkillGlobally", "cloud-download"),
      mk("Install skill into this workspace", "polis.installSkillWorkspace", "folder-active"),
      mk("Route an open contract", "polis.route", "git-compare"),
      mk("Open CONSTITUTION.md", "polis.openConstitution", "law"),
    ];
  }
}

// ───────────────────────── activate ─────────────────────────

function activate(context) {
  const contracts = new DirProvider("contracts/open", "No open contracts");
  const citizens = new DirProvider("citizens", "No citizens yet");
  vscode.window.registerTreeDataProvider("polisContracts", contracts);
  vscode.window.registerTreeDataProvider("polisCitizens", citizens);
  vscode.window.registerTreeDataProvider("polisActions", new ActionsProvider());

  const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  status.command = "polis.route";
  function updateStatus() {
    const root = polisRoot();
    if (hasPolis(root)) {
      let n = 0;
      try { n = fs.readdirSync(path.join(root, "_polis", "contracts", "open")).filter((f) => f.endsWith(".md")).length; } catch (_) { /* */ }
      status.text = `$(circuit-board) Polis: ${n} open`;
      status.tooltip = "Polis Protocol — click to route an open contract";
      status.show();
    } else {
      status.hide();
    }
  }

  const refresh = () => { contracts.refresh(); citizens.refresh(); updateStatus(); };

  context.subscriptions.push(
    vscode.commands.registerCommand("polis.init", () => cmdInit(context)),
    vscode.commands.registerCommand("polis.installSkillGlobally", () => cmdInstallSkillGlobally(context)),
    vscode.commands.registerCommand("polis.installSkillWorkspace", () => cmdInstallSkillWorkspace(context)),
    vscode.commands.registerCommand("polis.route", () => cmdRoute(context)),
    vscode.commands.registerCommand("polis.openConstitution", () => cmdOpenConstitution()),
    vscode.commands.registerCommand("polis.refresh", refresh),
    status
  );

  // React to file changes under _polis/
  const root = polisRoot();
  if (root) {
    const watcher = vscode.workspace.createFileSystemWatcher(
      new vscode.RelativePattern(root, "_polis/**/*.md"));
    watcher.onDidCreate(refresh);
    watcher.onDidDelete(refresh);
    watcher.onDidChange(refresh);
    context.subscriptions.push(watcher);
  }

  updateStatus();
}

function deactivate() {}

module.exports = { activate, deactivate };
