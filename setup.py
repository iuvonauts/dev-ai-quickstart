#!/usr/bin/env python3
import sys
from pathlib import Path
from getpass import getpass

# --- Helpers ---

def get_env_value(path: Path, key: str):
    """Reads a specific key from a .env file without regex."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip().startswith(f"{key}="):
            parts = line.split("=", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return None


def ask(prompt, default=None, secret=False):
    """Helper for interactive prompts. Secrets with defaults show [set]."""
    display_default = default
    if secret and default:
        display_default = "set"

    label = f"{prompt} [{display_default}]" if display_default else prompt
    val = getpass(f"{label}: ") if secret else input(f"{label}: ")

    # If user just hits enter, return the original default (the real key)
    return val.strip() or default


def update_env(path: Path, key: str, value: str):
    """Updates or appends a KEY=VALUE pair in .env without regex."""
    if not value:
        return
    if not path.exists():
        path.touch()

    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    found = False

    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def _strip_toml_comment(value: str) -> str:
    in_quotes = False
    escaped = False
    out = []
    for ch in value:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quotes:
            out.append(ch)
            escaped = True
            continue
        if ch == "\"":
            in_quotes = not in_quotes
            out.append(ch)
            continue
        if ch == "#" and not in_quotes:
            break
        out.append(ch)
    return "".join(out).strip()


def _toml_unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == "\"" and value[-1] == "\"":
        return value[1:-1]
    return value


def toml_get(lines: list[str], section: str | None, key: str) -> str | None:
    current_section = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            continue
        if section is not None and current_section != section:
            continue
        if section is None and current_section is not None:
            continue
        if "=" not in line:
            continue
        left, right = line.split("=", 1)
        if left.strip() != key:
            continue
        return _toml_unquote(_strip_toml_comment(right))
    return None


def toml_set(lines: list[str], section: str | None, key: str, value: str) -> list[str]:
    if value is None or value == "":
        return lines

    desired_line = f'{key} = "{value}"'
    out: list[str] = []
    current_section = None
    section_found = section is None
    key_written = False

    def flush_missing_section():
        nonlocal section_found, key_written
        if section_found or section is None:
            return
        if out and out[-1].strip() != "":
            out.append("")
        out.append(f"[{section}]")
        out.append(desired_line)
        section_found = True
        key_written = True

    for raw in lines:
        line = raw.strip()
        is_header = line.startswith("[") and line.endswith("]")
        if is_header:
            header_name = line[1:-1].strip()
            if section is not None and current_section == section and not key_written:
                out.append(desired_line)
                key_written = True
            if section is not None and not section_found and header_name != section:
                # Still haven't seen the desired section; keep going.
                pass
            current_section = header_name
            if section is not None and current_section == section:
                section_found = True
            out.append(raw)
            continue

        in_target_section = (section is None and current_section is None) or (section is not None and current_section == section)
        if in_target_section and not line.startswith("#") and "=" in line:
            left, _right = line.split("=", 1)
            if left.strip() == key:
                out.append(desired_line)
                key_written = True
                continue

        out.append(raw)

    if section is not None and not section_found:
        flush_missing_section()
    elif section is not None and section_found and not key_written:
        if out and out[-1].strip() != "":
            out.append("")
        out.append(desired_line)
    elif section is None and not key_written:
        # Insert near the top (after initial comments/blank lines).
        insert_at = 0
        for i, raw in enumerate(out):
            stripped = raw.strip()
            if stripped and not stripped.startswith("#"):
                insert_at = i
                break
            insert_at = i + 1
        out.insert(insert_at, desired_line)

    return out


# --- Main Flow ---

def main():
    repo_root = Path(__file__).parent.resolve()
    home = Path.home()
    code_dir = home / "code"
    codex_dir = home / ".codex"

    code_dir.mkdir(exist_ok=True)
    codex_dir.mkdir(exist_ok=True)

    env_target = code_dir / ".env"
    cfg_target = codex_dir / "config.toml"

    # Deploy templates
    if not env_target.exists():
        env_target.write_text((repo_root / ".setup/.env.example").read_text())
        print(f"Created {env_target}")

    if not cfg_target.exists():
        cfg_target.write_text((repo_root / ".setup/config.toml.example").read_text())
        print(f"Created {cfg_target}")

    toml_lines = cfg_target.read_text(encoding="utf-8").splitlines()

    print("\n--- Codex Configuration ---")
    print("Press Enter to keep existing values.")

    cur_profile = toml_get(toml_lines, None, "profile") or "azure"
    profile = ask("Select Profile (azure/chatgpt/custom)", cur_profile).lower()
    if profile not in {"azure", "chatgpt", "custom"}:
        print("❌ Invalid profile. Use azure, chatgpt, or custom.")
        sys.exit(1)
    toml_lines = toml_set(toml_lines, None, "profile", profile)

    if profile == "azure":
        cur_url = toml_get(toml_lines, "model_providers.azure", "base_url")
        url = ask("Azure Endpoint", cur_url)
        if url:
            toml_lines = toml_set(toml_lines, "model_providers.azure", "base_url", url)

        cur_model = toml_get(toml_lines, "profiles.azure", "model")
        model = ask("Azure Deployment/Model Name", cur_model)
        if model:
            toml_lines = toml_set(toml_lines, "profiles.azure", "model", model)

        cur_key = get_env_value(env_target, "AZURE_API_KEY")
        key = ask("Azure API Key", cur_key, secret=True)
        update_env(env_target, "AZURE_API_KEY", key)

    elif profile == "custom":
        cur_url = toml_get(toml_lines, "model_providers.custom", "base_url")
        url = ask("Custom Endpoint", cur_url)
        if url:
            toml_lines = toml_set(toml_lines, "model_providers.custom", "base_url", url)

        cur_model = toml_get(toml_lines, "profiles.custom", "model")
        model = ask("Custom Model Name", cur_model)
        if model:
            toml_lines = toml_set(toml_lines, "profiles.custom", "model", model)

        cur_key = get_env_value(env_target, "CUSTOM_API_KEY")
        key = ask("Custom API Key (optional)", cur_key, secret=True)
        update_env(env_target, "CUSTOM_API_KEY", key)

    cfg_target.write_text("\n".join(toml_lines) + "\n", encoding="utf-8")

    print("\n--- GitHub Access ---")
    cur_pat = get_env_value(env_target, "GITHUB_PAT")
    pat = ask("GitHub PAT (optional)", cur_pat, secret=True)
    update_env(env_target, "GITHUB_PAT", pat)

    print("\n✅ Setup complete. Run `code .` and select 'Reopen in Container'.")


if __name__ == "__main__":
    main()
