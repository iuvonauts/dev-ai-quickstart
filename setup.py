#!/usr/bin/env python3
import sys
from getpass import getpass
from pathlib import Path

DEFAULT_AZURE_BASE_URL = "https://<your-azure-openai-resource>.openai.azure.com/openai/v1"
DEFAULT_AZURE_MODEL = "gpt-5.2"
DEFAULT_CUSTOM_BASE_URL = "<your-openai-compatible-base-url>"
DEFAULT_CUSTOM_MODEL = "<your-model>"


def ask(prompt: str, default: str | None = None, *, secret: bool = False) -> str | None:
    display_default = "set" if (secret and default) else default
    label = f"{prompt} [{display_default}]" if display_default else prompt
    val = getpass(f"{label}: ") if secret else input(f"{label}: ")
    out = val.strip()
    return out if out else default


def toml_quote(value: str) -> str:
    # Minimal quoting for TOML basic strings.
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f"\"{value}\""


def toml_set_existing(lines: list[str], section: str | None, key: str, value: str) -> bool:
    """Set a TOML key that already exists in the template (no add/merge logic)."""
    wanted = f"{key} = {toml_quote(value)}"
    current_section: str | None = None
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip()
            continue

        if section is None:
            if current_section is not None:
                continue
        else:
            if current_section != section:
                continue

        if stripped.startswith(f"{key} ="):
            indent = raw[: len(raw) - len(raw.lstrip(" "))]
            lines[i] = indent + wanted
            return True
    return False


def write_devcontainer_env(path: Path, template_path: Path, *, azure_key: str, custom_key: str, gh_token: str):
    lines = template_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("AZURE_API_KEY="):
            out.append(f"AZURE_API_KEY={azure_key}")
        elif line.startswith("CUSTOM_API_KEY="):
            out.append(f"CUSTOM_API_KEY={custom_key}")
        elif line.startswith("GH_TOKEN="):
            out.append(f"GH_TOKEN={gh_token}")
        else:
            out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).parent.resolve()
    home = Path.home()
    code_dir = home / "code"
    codex_dir = home / ".codex"

    env_target = code_dir / "devcontainer.env"
    netrc_target = code_dir / "devcontainer.netrc"
    cfg_target = codex_dir / "config.toml"

    existing = [p for p in (env_target, netrc_target, cfg_target) if p.exists()]
    if existing:
        print("❌ Refusing to overwrite existing files:")
        for p in existing:
            print(f"  - {p}")
        print("\nDelete them if you want to re-run setup.")
        return 1

    code_dir.mkdir(exist_ok=True)
    codex_dir.mkdir(exist_ok=True)

    print("\n--- Codex Configuration ---")
    profile = (ask("Select Profile (azure/chatgpt/custom)", "azure") or "azure").lower()
    if profile not in {"azure", "chatgpt", "custom"}:
        print("❌ Invalid profile. Use azure, chatgpt, or custom.")
        return 1

    azure_base_url = DEFAULT_AZURE_BASE_URL
    azure_model = DEFAULT_AZURE_MODEL
    custom_base_url = DEFAULT_CUSTOM_BASE_URL
    custom_model = DEFAULT_CUSTOM_MODEL

    azure_key = ""
    custom_key = ""

    if profile == "azure":
        azure_base_url = ask("Azure Endpoint", DEFAULT_AZURE_BASE_URL) or DEFAULT_AZURE_BASE_URL
        azure_model = ask("Azure Deployment/Model Name", DEFAULT_AZURE_MODEL) or DEFAULT_AZURE_MODEL
        azure_key = ask("Azure API Key", None, secret=True) or ""
    elif profile == "custom":
        custom_base_url = ask("Custom Endpoint", DEFAULT_CUSTOM_BASE_URL) or DEFAULT_CUSTOM_BASE_URL
        custom_model = ask("Custom Model Name", DEFAULT_CUSTOM_MODEL) or DEFAULT_CUSTOM_MODEL
        custom_key = ask("Custom API Key (optional)", None, secret=True) or ""

    print("\n--- GitHub Access ---")
    gh_token = ask("GitHub PAT (optional)", None, secret=True) or ""

    # 1) devcontainer.env
    write_devcontainer_env(
        env_target,
        repo_root / ".setup/devcontainer.env.example",
        azure_key=azure_key,
        custom_key=custom_key,
        gh_token=gh_token,
    )
    print(f"Created {env_target}")

    # 2) devcontainer.netrc
    netrc_lines = ["machine github.com", "  login x-access-token"]
    if gh_token:
        netrc_lines.append(f"  password {gh_token}")
    netrc_target.write_text("\n".join(netrc_lines) + "\n", encoding="utf-8")
    try:
        netrc_target.chmod(0o600)
    except OSError:
        pass
    print(f"Created {netrc_target}")

    # 3) ~/.codex/config.toml
    cfg_lines = (repo_root / ".setup/config.toml.example").read_text(encoding="utf-8").splitlines()
    ok = True
    ok &= toml_set_existing(cfg_lines, None, "profile", profile)
    ok &= toml_set_existing(cfg_lines, "profiles.azure", "model", azure_model)
    ok &= toml_set_existing(cfg_lines, "model_providers.azure", "base_url", azure_base_url)
    ok &= toml_set_existing(cfg_lines, "profiles.custom", "model", custom_model)
    ok &= toml_set_existing(cfg_lines, "model_providers.custom", "base_url", custom_base_url)
    if not ok:
        print("❌ Failed to update .setup/config.toml.example (missing expected keys/sections).")
        return 1
    cfg_target.write_text("\n".join(cfg_lines) + "\n", encoding="utf-8")
    print(f"Created {cfg_target}")

    print("\n✅ Setup complete. Run `code .` and select 'Reopen in Container'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
