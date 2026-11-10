---
name: qa-ci-cd-pipelines
description: Configures automated CI/CD pipelines. Use when automating test execution in GitHub Actions or GitLab CI. Not for writing the test scripts themselves.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA CI/CD Pipeline Automation

## Purpose
Automates the execution of test suites in the cloud on code changes, preventing regressions before code is merged.

## When to Use
- Setting up GitHub Actions or GitLab CI workflows.
- Configuring parallel test execution or artifact uploads.
## When NOT to Use
- For writing the tests themselves.

## Prerequisites
- The project has a test suite ready to run via CLI commands.

## Step-by-Step Instructions
1. **Identify Triggers:** Define when tests should run (e.g., `on: pull_request`).
2. **Configure Environment:** Set up the OS, Node/Python versions, and necessary services (e.g., Redis, DB).
3. **Manage Dependencies:** Add steps for caching and installing dependencies (e.g., `npm ci`).
4. **Execute Tests:** Run the specific test commands.
5. **Artifacts & Reporting:** Configure the pipeline to upload test reports and screenshots on failure.

## Validation Criteria
- The pipeline must fail (exit code > 0) if the test suite fails.

## Safety Considerations
- Never hardcode secrets in the pipeline file; always reference environment variables/secrets managers.

## Expected Output
A complete YAML pipeline configuration file (e.g., `.github/workflows/qa.yml`).

## Examples
**User:** "Automate our Playwright tests on GitHub Actions."
**Agent:** Generates a YAML file that checks out the repo, installs Playwright browsers, runs the test suite, and uploads the `playwright-report` directory as a build artifact.