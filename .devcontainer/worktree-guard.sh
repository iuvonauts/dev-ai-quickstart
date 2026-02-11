#!/usr/bin/env bash
set -euo pipefail

RC_BASH="${HOME}/.bashrc"
RC_ZSH="${HOME}/.zshrc"
MARKER="# Dev AI Quickstart: Worktree Guard"

GUARD_FUNCTION=$(cat <<'EOF'
# Dev AI Quickstart: Worktree Guard
git() {
  if [[ "${GIT_WORKTREE_UNLOCK:-}" == "1" ]]; then
    command git "$@"
    return $?
  fi

  if [[ "${1:-}" == "switch" || "${1:-}" == "checkout" ]]; then
    # Blocks when this is a linked worktree ('.git' is a file) or when the main
    # worktree has linked worktrees ('.git/worktrees' exists).
    if [[ -f ".git" || -d ".git/worktrees" ]]; then
      echo "Blocked: use git worktree (override: GIT_WORKTREE_UNLOCK=1)." >&2
      return 1
    fi
  fi

  command git "$@"
}
EOF
)

install_guard_into_rc() {
  local rc="$1"

  [[ -f "${rc}" ]] || touch "${rc}"
  if grep -Fq "${MARKER}" "${rc}"; then
    echo "Worktree guard already present in ${rc}"
    return 0
  fi

  printf "\n%s\n" "${GUARD_FUNCTION}" >> "${rc}"
  echo "Installed worktree guard into ${rc}"
}

install_guard_into_rc "${RC_BASH}"
install_guard_into_rc "${RC_ZSH}"
