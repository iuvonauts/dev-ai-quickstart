# Dev AI Quickstart

This repository creates a ready-to-use AI coding environment in VS Code using a Dev Container. A Dev Container is a pre-built, isolated development environment that keeps your tools and dependencies separate from your computer.

This repo creates a starting development environment for your project. Your actual project code should go in `src/` and can be its own git repository. Running setup will create a host config so your configuration is reused across all Dev Containers in your environment without additional configuration.

## What's In This Quickstart
- A pre-configured Docker-based Dev Container based on `mcr.microsoft.com/devcontainers/universal:linux`.
- Docker access inside the Dev Container so the agent can spin up new environments to test code.
- The OpenAI Codex coding extension (`openai.chatgpt`), configured via profiles to use Azure, ChatGPT sign-in, or a custom OpenAI-compatible endpoint.
- A setup script (`setup.py`) to configure the initial environment.

## Before You Start (Important)
This quickstart requires a folder named `code` in your home directory (Linux/WSL/macOS) where your repos will be stored.

In the steps below:
- `~` means "your home folder" (Linux/WSL: usually `/home/<yourname>`, macOS: usually `/Users/<yourname>`).
- Commands in `bash` blocks go in a Linux/WSL/macOS terminal.
- Commands in `powershell` blocks go in Windows PowerShell.
- On Windows, to launch WSL after installation, open "PowerShell" and run:
   ```powershell
   wsl
   ```

## Setup (Windows, macOS, and Linux)

### 1) Install WSL (Windows only)
1. Right-click the Start menu icon and select "Terminal (Admin)".
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your computer when prompted.
4. Open "Ubuntu" from the Start menu and create a username and password.

### 2) Install Required Software
1. Install VS Code with defaults:
   https://code.visualstudio.com/
2. In VS Code, install:
   - Dev Containers: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
3. Install Docker with defaults:
   - Windows/macOS: Docker Desktop https://www.docker.com/products/docker-desktop/
      * You can safely ignore any prompts from Docker Desktop to create an account or log in.
   - Linux: Docker Engine https://docs.docker.com/engine/install/
4. Install Git:
   - Linux/WSL:
     ```bash
     sudo apt update \
         && sudo apt install -y git \
         && git config --global init.defaultBranch main
     ```
   - macOS: open Terminal, run `git --version`, and follow the prompt to install developer tools if asked.

### 3) Clone the Template
In Linux/WSL/macOS:

1) Pick a repo name (used in the commands below):
```bash
REPO="my-repo"
```

2) Make the parent folder and clone the template into `main`:
```bash
mkdir -p ~/code/"$REPO" \
   && cd ~/code/"$REPO" \
   && git clone https://github.com/iuvonauts/dev-ai-quickstart.git main
```

3) Detach from the template and start fresh git history:
```bash
cd ~/code/"$REPO"/main \
  && git remote remove origin \
  && rm -rf .git \
  && git init
```

### 4) Run Setup Script
From the repo folder in Linux/WSL/macOS, run:
```bash
python3 setup.py
```
This script creates the default Codex extension configuration files (`~/code/devcontainer.env`, `~/code/devcontainer.netrc`, and `~/.codex/config.toml`) and prompts you for your preferred profile (`Azure/ChatGPT/Custom`) and any required values. It writes `~/.codex/config.toml` from `.setup/config.toml.example` and fills in the profile/endpoint/model values.
It will not overwrite existing files; you will need to delete them if you want to re-run setup.

Included profiles:
- **Azure**: Azure OpenAI endpoint + API key; requires `AZURE_API_KEY`. The setup script will also prompt you for the endpoint and model to write into `~/.codex/config.toml`. For iuvo, the endpoint and key are stored together in internal documentation/password manager as `Azure coding agent API key`.
- **ChatGPT**: OpenAI sign-in; you will be prompted to log in when you first use Codex in VS Code.
- **Custom**: Any OpenAI-compatible endpoint (local or hosted). The setup script will prompt you for the endpoint and model to write into `~/.codex/config.toml`, and (optionally) `CUSTOM_API_KEY`. Example local endpoint: `http://host.docker.internal:8080/v1`.

You will also be prompted for an optional GitHub Personal Access Token to store in `~/code/devcontainer.netrc` for GitHub access inside the Dev Container (for example: cloning private repos, pushing code, or using GitHub APIs). This can be created at https://github.com/settings/tokens.

**Treat all keys like passwords! Do not commit them or share them in chat!**

### 5) Launch the Dev Container
1. From the same folder in Linux/WSL/macOS, run:
   ```bash
   code .
   ```
   Click through any "Trust this repo/folder" prompts.
3. When VS Code prompts, click **Reopen in Container**.
   If you do not see the prompt:
   1. Open the Command Palette (Ctrl+Shift+P).
   2. Run: `Dev Containers: Reopen in Container`.
4. Wait for the container to build (first time can take several minutes).

## Agent Skills & Tools
Most coding agents support Agent Skills (https://agentskills.io/). Agent Skills ensure agents apply consistent instructions for specific tasks. Skills are stored in `.codex/skills/<skill-name>/`. The skills `$skill-creator` and `$skill-installer` are included by default with the Codex extension. To add additional skills, you can browse OpenAI's curated skills catalog at https://github.com/openai/skills, find other skills created by the community, or create your own skills for specific tasks.

This quickstart also includes two MCP tools in `~/.codex/config.toml` (created from `.setup/config.toml.example`):
- `context7`: Pulls up-to-date library documentation and code examples. The agent will use this tool when answering API/library questions to avoid outdated information.
- `semgrep`: Runs static security scanning on code and returns actionable findings. Ask the agent to use this tool for security reviews and before publishing.

## Repo Layout
```text
.
├─ README.md                  # Getting started
├─ AGENTS.md                  # Agent context entry point
├─ .agents/
│  ├─ overview.md             # Repo purpose and layout
│  ├─ environment.md          # Devcontainer/tooling notes
│  ├─ status.md               # Current status
│  ├─ outstanding.md          # Backlog
│  └─ conventions.md          # Conventions and norms
├─ .codex/
│  ├─ sessions/               # Agent chat sessions logs
│  └─ skills/                 # Agent skills
├─ .devcontainer/
│  └─ devcontainer.json       # Dev Container definition
├─ .vscode/
│  └─ settings.json           # VS Code settings
├─ .setup/
│  ├─ devcontainer.env.example # Example env vars (copied to ~/code/devcontainer.env by setup script)
│  ├─ devcontainer.netrc      # Example netrc entry for GitHub
│  └─ config.toml.example     # Example Codex config (copied to ~/.codex/config.toml by setup script)
├─ setup.py                   # Writes ~/code/devcontainer.env, ~/code/devcontainer.netrc, and ~/.codex/config.toml
└─ src/                       # Your production repo
```
