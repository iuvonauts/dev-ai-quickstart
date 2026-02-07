# Agent Working Notes

_Last updated: 2026-02-05_

This file is a lightweight index of the repo context, current priorities, and working agreements. Keep it short, update the date when material changes, and move details into the linked pages.

## How To Use
- Read `.agents/overview.md` to understand the goal, scope, and layout.
- Check `.agents/status.md` for current state and any blockers.
- Review `.agents/outstanding.md` for the backlog and open questions.
- Follow `.agents/conventions.md` for project norms.
- Update `.agents/environment.md` when devcontainer or tooling changes.

## Environment Notes
- For API or library questions, consult up-to-date documentation tools before answering.
- For security analysis, favor static analysis tools when present and summarize actionable findings.
- GitHub credentials are mounted to `/home/codespace/.netrc`.
- Docker is available inside the devcontainer for running code/test environments.
- `HOST_WORKSPACE` is set to the host path of the repo for docker-outside-docker bind mounts.
- The production codebase should live in `src/` as its own repo; this repo only provisions the development environment.
- Codex session logs are written under `.codex/sessions/`. This template keeps the folder empty; commit sessions in your derived repo only if user wants to preserve conversations.
- Project-local agent skills live under `.codex/skills/`.

## Quick Map
- [.agents/overview.md](.agents/overview.md)
- [.agents/environment.md](.agents/environment.md)
- [.agents/status.md](.agents/status.md)
- [.agents/outstanding.md](.agents/outstanding.md)
- [.agents/conventions.md](.agents/conventions.md)
