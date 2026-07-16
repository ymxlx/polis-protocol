#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install Polis Protocol into a project.

Usage:
  curl -fsSL https://raw.githubusercontent.com/ymxlx/polis-protocol/main/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/ymxlx/polis-protocol/main/install.sh | bash -s -- --agent-id claude-research-myapp

Options:
  --project-root PATH    Project to initialize. Default: current directory
  --agent-id ID          Founding citizen id. Default: agent-<project-folder>
  --project-name NAME    Human-readable project name. Default: folder name
  --vendor NAME          anthropic, openai, google, meta, mistral, other. Default: other
  --model NAME           Model identifier. Default: unknown-model
  --tool NAME            Tool name. Default: ai-agent
  --force                Overwrite existing Polis files
  -h, --help             Show this help

Environment variables with the same intent are also supported:
  POLIS_PROJECT_ROOT, POLIS_AGENT_ID, POLIS_PROJECT_NAME, POLIS_VENDOR,
  POLIS_MODEL, POLIS_TOOL
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Polis install error: missing required command '$1'." >&2
    exit 1
  fi
}

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
}

default_agent_id() {
  local project_name="$1"
  local slug
  slug="$(slugify "$project_name")"
  if [ -z "$slug" ]; then
    slug="project"
  fi
  slug="agent-$slug"
  if [ "${#slug}" -lt 8 ]; then
    slug="${slug}-polis"
  fi
  printf '%s' "${slug:0:40}"
}

PROJECT_ROOT="${POLIS_PROJECT_ROOT:-$PWD}"
PROJECT_NAME="${POLIS_PROJECT_NAME:-}"
AGENT_ID="${POLIS_AGENT_ID:-}"
VENDOR="${POLIS_VENDOR:-other}"
MODEL="${POLIS_MODEL:-unknown-model}"
TOOL="${POLIS_TOOL:-ai-agent}"
FORCE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --agent-id)
      AGENT_ID="$2"
      shift 2
      ;;
    --project-name)
      PROJECT_NAME="$2"
      shift 2
      ;;
    --vendor)
      VENDOR="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --tool)
      TOOL="$2"
      shift 2
      ;;
    --force)
      FORCE="--force"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_cmd curl
require_cmd tar
require_cmd python3

PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
if [ -z "$PROJECT_NAME" ]; then
  PROJECT_NAME="$(basename "$PROJECT_ROOT")"
fi
if [ -z "$AGENT_ID" ]; then
  AGENT_ID="$(default_agent_id "$PROJECT_NAME")"
fi

TMPDIR="$(mktemp -d "${TMPDIR:-/tmp}/polis-install.XXXXXX")"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "Downloading Polis Protocol..."
curl -fsSL "https://github.com/ymxlx/polis-protocol/archive/refs/heads/main.tar.gz" \
  | tar -xz -C "$TMPDIR" --strip-components=1

echo "Founding polis in $PROJECT_ROOT"
python3 "$TMPDIR/scripts/init_polis.py" \
  --project-root "$PROJECT_ROOT" \
  --agent-id "$AGENT_ID" \
  --vendor "$VENDOR" \
  --model "$MODEL" \
  --tool "$TOOL" \
  --project-name "$PROJECT_NAME" \
  $FORCE

cat <<EOF
Polis install complete.

Next:
  1. Open $PROJECT_ROOT/_polis/index.md
  2. Edit $PROJECT_ROOT/_polis/citizens/$AGENT_ID/capability_card.yml
  3. Ask another AI tool to enter the project; it will find CLAUDE.md, AGENTS.md, or GEMINI.md
EOF
