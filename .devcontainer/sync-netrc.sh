#!/usr/bin/env bash
set -euo pipefail

NETRC_PATH="${HOME}/.netrc"
GH_TOKEN_VALUE="${GH_TOKEN:-}"

if [[ -z "${GH_TOKEN_VALUE}" ]]; then
  rm -f "${NETRC_PATH}"
  exit 0
fi

cat > "${NETRC_PATH}" <<EOF
machine github.com
  login x-access-token
  password ${GH_TOKEN_VALUE}
EOF

chmod 600 "${NETRC_PATH}"
