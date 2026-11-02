---
name: dockly
description: Analyzes project dependencies to generate Dockerfile and docker-compose.yml. Use when the user asks to deploy, dockerize, or put the app on a server.
metadata:
  categories: Deployment, DevOps
  maintainers: IZ1KG
---

# Dockly

## Prerequisites
- Docker and Docker Compose installed on the user's machine (if testing locally).
- Standard project configuration files exist in the directory (e.g., `package.json`, `requirements.txt`, `.csproj`).

## When to Use
Use this skill when the user asks to "deploy the app", "dockerize the project", "put this on a server", or when they struggle with local environment differences (e.g., "it works on my machine but not elsewhere"). It is designed to abstract away containerization complexities for users without DevOps experience.

## Instructions
When invoked, you must follow these steps in strict order:
1. **Analyze Stack:** Scan the project's root directory to identify the primary language and framework. If this is a monorepo or has multiple subfolders, ask the user which specific service to dockerize first.
2. **Scaffold Dockerfile:** Create an optimized, multi-stage `Dockerfile` (e.g., use `node:alpine` with `npm run build` for Node.js, or standard python base for Python). You MUST generate a `.dockerignore` file to prevent copying dependencies (`node_modules`, `venv`, `bin/`, `obj/`, `.git`). Critically, also exclude `.env*` and credential files. explicitly tell the user to keep secrets out of the image.
3. **Scaffold Compose:** Create a `docker-compose.yml` for the main application and backing services (e.g., PostgreSQL, MongoDB). Always use environment variables for credentials (e.g., `${POSTGRES_PASSWORD}`), NEVER hard-code passwords in the compose file.
4. **Validate & Report:** Attempt to run `docker compose config` (and `docker build` if Docker is available) to validate the configuration. Report the results to the user. If it cannot run, explain why. Finally, tell them the command to run: `docker compose up -d`.

**Risk & Permissions Note:** 
- NEVER overwrite existing `Dockerfile` or `docker-compose.yml` files without explicit user confirmation.
- Alert the user that running databases via Docker Compose locally will bind to default ports (e.g., 5432, 27017), which might conflict with local installations on their machine.

## Examples
**User:** "Can you help me get this Next.js app ready for my VPS?"
**Agent:** Invokes Dockly, creates a multi-stage Dockerfile and a docker-compose.yml for the Next.js app, adds `.dockerignore` (including `.env*`), uses env vars for secrets, runs `docker compose config`, and provides the exact `docker compose up -d` command.