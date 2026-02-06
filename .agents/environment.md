# Environment

## Dev Container
- Base image: `mcr.microsoft.com/devcontainers/universal:linux`
- Feature: Docker-outside-of-Docker so the agent can run `docker`/`docker compose` inside the Dev Container to spin up test containers for the `src/` repo (uses your host Docker engine).
- VS Code extensions:
  - `openai.chatgpt` (Codex)

## Local Requirements
- Docker Desktop (or compatible Docker runtime).
- VS Code with the Dev Containers extension, or GitHub Codespaces.

## Environment Files
- The devcontainer loads `${HOME}/code/devcontainer.env` via `--env-file`.
- GitHub credentials are mounted from `${HOME}/code/devcontainer.netrc` to `/home/codespace/.netrc`.
- Ensure the files exist or update the devcontainer configuration.

## Docker-Outside-Docker
- `HOST_WORKSPACE` points to the host path of the repo so Docker bind mounts work when running `docker compose` inside the devcontainer.

## Codex Configuration
- Host config mounted into `/home/codespace/.codex`.
- Session logs mounted from `.codex/sessions` in the repo.

## Setup Script
- Run `python3 setup.py` from the repo to create `~/code/devcontainer.env`, `~/code/devcontainer.netrc`, and `~/.codex/config.toml` (it refuses to overwrite existing files).

## Worktree Guard
- `.devcontainer/worktree-guard.sh` can install a guard that blocks `git switch` / `git checkout` in this repo.
