#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

host_env="${HOME}/code/.env"
host_codex_dir="${HOME}/.codex"
host_codex_config="${host_codex_dir}/config.toml"

mkdir -p "${HOME}/code"
mkdir -p "${host_codex_dir}"

env_example="${repo_root}/setup/.env.example"
codex_config_example="${repo_root}/setup/config.toml.example"

if [[ ! -f "${env_example}" ]]; then
  echo "Missing ${env_example}" >&2
  exit 1
fi

if [[ ! -f "${codex_config_example}" ]]; then
  echo "Missing ${codex_config_example}" >&2
  exit 1
fi

if [[ ! -f "${host_env}" ]]; then
  cp "${env_example}" "${host_env}"
  echo "Created ${host_env} from setup/.env.example"
else
  echo "Found ${host_env}"
fi

if [[ ! -f "${host_codex_config}" ]]; then
  cp "${codex_config_example}" "${host_codex_config}"
  echo "Created ${host_codex_config} from setup/config.toml.example"
else
  echo "Found ${host_codex_config}"
fi

get_env_value() {
  local key="$1"
  local file="$2"
  if [[ ! -f "${file}" ]]; then
    return 0
  fi
  grep -E "^${key}=" "${file}" | head -n 1 | sed -E "s/^${key}=//" || true
}

get_toml_value_in_section() {
  local section="$1"
  local key="$2"
  local file="$3"

  awk -v section="${section}" -v key="${key}" '
    BEGIN { in_section = 0 }
    {
      raw = $0
      line = raw
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)

      if (substr(line, 1, 1) == "[" && substr(line, length(line), 1) == "]") {
        section_name = substr(line, 2, length(line) - 2)
        in_section = (section_name == section)
        next
      }

      if (in_section && line ~ "^[[:space:]]*" key "[[:space:]]*=") {
        value = raw
        sub("^[[:space:]]*" key "[[:space:]]*=[[:space:]]*", "", value)
        sub(/^[[:space:]]+/, "", value)
        sub(/[[:space:]]+$/, "", value)
        gsub(/^"|"$/, "", value)
        print value
        exit
      }
    }
  ' "${file}" || true
}

update_toml_key_in_section() {
  local section="$1"
  local key="$2"
  local value="$3"
  local file="$4"

  if [[ -z "${value}" ]]; then
    return 0
  fi

  if [[ "${value}" == *\"* ]]; then
    echo "Refusing to write ${key}: value contains a double-quote (\")." >&2
    exit 1
  fi

  local tmp
  tmp="$(mktemp)"

  awk -v section="${section}" -v key="${key}" -v val="${value}" '
    BEGIN { in_section = 0; seen_section = 0; updated = 0 }
    {
      raw = $0
      line = raw
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)

      if (substr(line, 1, 1) == "[" && substr(line, length(line), 1) == "]") {
        if (in_section && !updated) {
          print key " = \"" val "\""
          updated = 1
        }

        section_name = substr(line, 2, length(line) - 2)
        in_section = (section_name == section)
        if (in_section) { seen_section = 1 }

        print raw
        next
      }

      if (in_section && line ~ "^[[:space:]]*" key "[[:space:]]*=") {
        print key " = \"" val "\""
        updated = 1
        next
      }

      print raw
    }
    END {
      if (in_section && !updated) {
        print key " = \"" val "\""
        updated = 1
      }
      if (!seen_section) {
        print ""
        print "[" section "]"
        print key " = \"" val "\""
      }
    }
  ' "${file}" > "${tmp}"

  mv "${tmp}" "${file}"
}

update_env_key() {
  local key="$1"
  local value="$2"
  local file="$3"

  if [[ -z "${value}" ]]; then
    return 0
  fi

  local tmp
  tmp="$(mktemp)"
  awk -v k="${key}" -v v="${value}" '
    BEGIN { found = 0 }
    $0 ~ ("^" k "=") { print k "=" v; found = 1; next }
    { print }
    END { if (!found) print k "=" v }
  ' "${file}" > "${tmp}"
  mv "${tmp}" "${file}"
}

read -r -p "Set default profile (azure/chatgpt/custom) [azure]: " profile_input
profile_input="${profile_input:-azure}"

case "${profile_input}" in
  azure|chatgpt|custom) ;;
  *) echo "Invalid profile. Use azure, chatgpt, or custom." >&2; exit 1 ;;
esac

existing_azure_base_url="$(get_toml_value_in_section "model_providers.azure" "base_url" "${host_codex_config}")"
existing_custom_base_url="$(get_toml_value_in_section "model_providers.custom" "base_url" "${host_codex_config}")"

existing_azure_key="$(get_env_value "AZURE_API_KEY" "${host_env}")"
existing_custom_key="$(get_env_value "CUSTOM_API_KEY" "${host_env}")"

existing_azure_model="$(get_toml_value_in_section "profiles.azure" "model" "${host_codex_config}")"
existing_custom_model="$(get_toml_value_in_section "profiles.custom" "model" "${host_codex_config}")"

echo "Leave a prompt blank to keep the existing value."

azure_endpoint=""
azure_model=""
azure_key=""
if [[ "${profile_input}" == "azure" ]]; then
  if [[ -n "${existing_azure_base_url}" && "${existing_azure_base_url}" != *"<"* ]]; then
    azure_endpoint="${existing_azure_base_url}"
  fi

  if [[ -z "${azure_endpoint}" || "${azure_endpoint}" == *"<"* ]]; then
    while [[ -z "${azure_endpoint}" ]]; do
      read -r -p "AZURE_ENDPOINT (required for azure profile, e.g. https://.../openai/v1): " azure_endpoint
    done
  else
    read -r -p "AZURE_ENDPOINT (optional): " azure_endpoint
  fi

  if [[ -n "${existing_azure_model}" && "${existing_azure_model}" != *"<"* ]]; then
    azure_model="${existing_azure_model}"
  else
    azure_model="gpt-5.2"
  fi

  read -r -p "AZURE_MODEL (optional) [${azure_model}]: " azure_model_input
  azure_model="${azure_model_input:-${azure_model}}"

  if [[ -z "${existing_azure_key}" ]]; then
    while [[ -z "${azure_key}" ]]; do
      read -r -s -p "AZURE_API_KEY (required for azure profile): " azure_key
      echo
    done
  else
    read -r -s -p "AZURE_API_KEY (optional): " azure_key
    echo
  fi
fi

custom_endpoint=""
custom_model=""
custom_key=""
if [[ "${profile_input}" == "custom" ]]; then
  if [[ -n "${existing_custom_base_url}" && "${existing_custom_base_url}" != *"<"* ]]; then
    custom_endpoint="${existing_custom_base_url}"
  fi

  if [[ -z "${custom_endpoint}" || "${custom_endpoint}" == *"<"* ]]; then
    while [[ -z "${custom_endpoint}" ]]; do
      read -r -p "CUSTOM_ENDPOINT (required for custom profile, e.g. http://host.docker.internal:8080/v1): " custom_endpoint
    done
  else
    read -r -p "CUSTOM_ENDPOINT (optional): " custom_endpoint
  fi

  if [[ -n "${existing_custom_model}" && "${existing_custom_model}" != *"<"* ]]; then
    custom_model="${existing_custom_model}"
  fi

  if [[ -z "${custom_model}" || "${custom_model}" == *"<"* ]]; then
    while [[ -z "${custom_model}" ]]; do
      read -r -p "CUSTOM_MODEL (required for custom profile, e.g. llama-3.1-8b-instruct): " custom_model
    done
  else
    read -r -p "CUSTOM_MODEL (optional): " custom_model
  fi

  if [[ -z "${existing_custom_key}" ]]; then
    while [[ -z "${custom_key}" ]]; do
      read -r -s -p "CUSTOM_API_KEY (required for custom profile; enter any text if not needed): " custom_key
      echo
    done
  else
    read -r -s -p "CUSTOM_API_KEY (optional): " custom_key
    echo
  fi
fi

read -r -s -p "GITHUB_PAT (optional): " github_pat
echo

update_env_key "AZURE_API_KEY" "${azure_key}" "${host_env}"
update_env_key "CUSTOM_API_KEY" "${custom_key}" "${host_env}"
update_env_key "GITHUB_PAT" "${github_pat}" "${host_env}"

awk -v prof="${profile_input}" 'BEGIN{set=0} $0 ~ "^profile[[:space:]]*=" {print "profile = \""prof"\""; set=1; next} {print} END{if(!set){print "profile = \""prof"\""}}' "${host_codex_config}" > "${host_codex_config}.tmp"
mv "${host_codex_config}.tmp" "${host_codex_config}"

update_toml_key_in_section "model_providers.azure" "base_url" "${azure_endpoint}" "${host_codex_config}"
update_toml_key_in_section "profiles.azure" "model" "${azure_model}" "${host_codex_config}"

if [[ "${profile_input}" == "custom" ]]; then
  update_toml_key_in_section "profiles.custom" "model_provider" "custom" "${host_codex_config}"
  update_toml_key_in_section "profiles.custom" "model" "${custom_model}" "${host_codex_config}"

  update_toml_key_in_section "model_providers.custom" "name" "Custom OpenAI-compatible" "${host_codex_config}"
  update_toml_key_in_section "model_providers.custom" "env_key" "CUSTOM_API_KEY" "${host_codex_config}"
  update_toml_key_in_section "model_providers.custom" "wire_api" "responses" "${host_codex_config}"
  update_toml_key_in_section "model_providers.custom" "base_url" "${custom_endpoint}" "${host_codex_config}"
fi

cat <<'MSG'
Next steps:
- Re-open VS Code and run "Dev Containers: Reopen in Container".
MSG
