#!/usr/bin/env bash
# 30-second tour of the Polis Protocol.
#
# Runs the learning router against the bundled research-team example and shows
# the moment that makes the protocol click: the router recommends *Gemini* for a
# Spanish-translation contract — not because a human opened her tab, but because
# settled contracts taught it she has the best track record on that work.
#
# No setup, no API keys, no install. Just:
#   bash scripts/demo.sh

set -euo pipefail

# Resolve repo root from this script's location, so it works from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
POLIS="${ROOT}/examples/research-team/_polis"
CONTRACT="${POLIS}/contracts/open/parent-newsletter-issue-3.md"

if ! command -v python3 >/dev/null 2>&1; then
  echo "This demo needs python3 (3.10+). Install it and re-run." >&2
  exit 1
fi

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
dim()  { printf "\033[2m%s\033[0m\n" "$1"; }

echo
bold "Polis Protocol — 30-second tour"
dim  "A three-citizen team: Claude (research), Codex (frontend), Gemini (translation)."
echo
bold "1. There is an open contract that needs Spanish translation."
dim  "   contracts/open/parent-newsletter-issue-3.md"
echo
bold "2. Ask the router who should take it — and to explain itself:"
dim  "   python3 scripts/route_contract.py --polis-root <example> --contract <above> --explain"
echo
sleep 1

# --seed 42 makes this tour reproducible. The router explores ~15% of the time
# (picking a non-leader to keep its judgment honest); a fixed seed lands on the
# exploit pick so the demo always tells the same story. Drop --seed to see the
# real stochastic behavior.
python3 "${ROOT}/scripts/route_contract.py" \
  --polis-root "${POLIS}" \
  --contract "${CONTRACT}" \
  --seed 42 \
  --explain

echo
bold "What just happened"
cat <<'EOF'
  Gemini wins — even though her self-rating is the same as the others on paper.
  She wins on `hist` (historical performance), because two settled contracts and
  a lesson ("the corporate word 'líder' reads wrong; use the movement loan-word
  'madrij'") taught the router she is the strongest Spanish translator on the team.

  Early in this project, Claude was the leader on that tag. The router moved the
  work. Nobody reassigned it. The team got better, and the routing followed.

  That is the whole idea. Everything else — capability cards, the chronicle,
  chavruta review, self-amending rules — exists to make that one loop trustworthy.
EOF
echo
bold "See the full worked example:"
dim  "  examples/research-team/   (3 citizens, a leader shift, a ratified amendment)"
bold "Start your own polis:"
dim  "  curl -fsSL https://raw.githubusercontent.com/yehudalevy-collab/polis-protocol/main/install.sh | bash"
echo
