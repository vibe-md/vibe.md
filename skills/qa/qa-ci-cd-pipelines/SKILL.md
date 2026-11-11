---
name: qa-ci-cd-pipelines
description: Configures automated CI/CD pipelines. Use when automating test execution in GitHub Actions or GitLab CI. Not for writing the test scripts themselves.
metadata:
  collection: vibe.md
  group: qa
---

# QA CI/CD Pipeline Automation

## Purpose
Automates test execution within continuous integration workflows.

## When to Use
- Setting up or updating GitHub Actions or GitLab CI configurations for testing.

## Step-by-Step Instructions
1. **Check Existing Workflows:** Search `.github/workflows/` or pipeline configurations to avoid duplicating existing setup.
2. **Define Triggers:** Configure triggers (e.g., `pull_request`, `push` to main).
3. **Draft Pipeline:** Create or update the workflow file with steps for dependency installation, test commands, and artifact uploading.
4. **Review with User:** Confirm environment variables and secret names before finalizing.

## Examples
**User:** "Run our E2E tests on GitHub Actions."
**Agent:** Checks existing workflows, drafts `.github/workflows/e2e.yml`, and sets up Playwright execution with artifact upload.