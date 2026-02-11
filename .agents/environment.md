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
- In-container auth surface:
- `GH_TOKEN` is for GitHub API/CLI interactions that read a token from env.
- `/home/codespace/.netrc` is for git-over-HTTPS operations (clone/fetch/push).
- These are provisioned by devcontainer setup and host mounts.

## Docker-Outside-Docker
- `HOST_WORKSPACE` points to the host path of the repo so Docker bind mounts work when running `docker compose` inside the devcontainer.

## Codex Configuration
- Host config mounted into `/home/codespace/.codex`.
- Session logs mounted from `.codex/sessions` in the repo.

## Setup Script
- `python3 setup.py` prepares host-side files consumed by the devcontainer; agents should rely on in-container paths/variables.
