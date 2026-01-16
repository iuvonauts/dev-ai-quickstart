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
- The devcontainer loads `${HOME}/code/.env` via `--env-file`.
- Ensure the file exists or update the devcontainer configuration.

## Codex Configuration
- Host config mounted into `/home/codespace/.codex`.
- Session logs mounted from `.codex/sessions` in the repo.
