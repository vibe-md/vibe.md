---
name: dockly
description: Analyzes project dependencies to generate Dockerfile and docker-compose.yml, simplifying containerization for vibe coders.
metadata:
  categories: Deployment, DevOps
  maintainers: IZ1KG
---

# Dockly

## When to Use
Use this skill when the user asks to "deploy the app", "dockerize the project", "put this on a server", or when they struggle with local environment differences (e.g., "it works on my machine but not elsewhere"). It is designed to abstract away containerization complexities for users without DevOps experience.

## Instructions
When invoked, you must follow these steps in strict order:
1. **Analyze Stack:** Scan the project's root directory to identify the primary language and framework (e.g., `package.json` for Node/React/Next.js, `requirements.txt` for Python, `.csproj` for .NET).
2. **Scaffold Dockerfile:** Create an optimized, multi-stage `Dockerfile`. You must generate a `.dockerignore` file to prevent copying dependencies like `node_modules`, `venv`, `bin/`, `obj/`, or `.git`.
3. **Scaffold Compose:** Create a `docker-compose.yml` that includes the main application and any backing services (e.g., PostgreSQL, MongoDB, Redis) referenced in the code or environment variables.
4. **Explain in Plain English:** Avoid deep DevOps jargon. Tell the user exactly what to do next: "I've prepared your app for deployment. Just make sure Docker is installed and run `docker compose up -d` in your terminal."

**Risk & Permissions Note:** 
- NEVER overwrite existing `Dockerfile` or `docker-compose.yml` files without explicit user confirmation.
- Alert the user that running databases via Docker Compose locally will bind to default ports (e.g., 5432, 27017), which might conflict with local installations on their machine.

## Examples
**User:** "Can you help me get this Next.js app ready for my VPS?"
**Agent:** Invokes Dockly, creates a multi-stage Dockerfile and a docker-compose.yml for the Next.js app, adds `.dockerignore`, and provides the exact `docker compose up -d` command.

**User:** "I want to dockerize this project."
**Agent:** Scans the directory, identifies a .NET 8 backend and a PostgreSQL dependency. Generates the necessary container configurations safely, warning the user about port 5432 before proceeding.