---
name: qa-accessibility-testing
description: Adds automated axe-core checks (contrast, alt text, ARIA) to UI tests. Use when auditing web pages for automated WCAG rules. Keyboard and screen-reader checks remain manual.
metadata:
  collection: vibe.md
  group: qa
---

# QA Accessibility Testing

## Purpose
Validates that web applications comply with automated accessibility standards using `axe-core`.

## When to Use
- When auditing web UI components or pages for automated WCAG rules (contrast, image alt attributes, ARIA roles).

## Prerequisites
- UI testing framework installed. Ask the user for confirmation before installing new packages (such as `@axe-core/playwright`).

## Step-by-Step Instructions
1. **Check Existing Setup:** Inspect the project to reuse the existing test runner. Ask the user before installing any new dependencies.
2. **Inject Axe:** Configure the test to run `axe-core` scans on target components or pages.
3. **Scan & Assert:** Validate automated rules (color contrast, missing alt text, ARIA attributes).
4. **Report Limitations:** Remind the user that keyboard navigation and screen-reader flows require manual testing.

## Safety Considerations
- Automated a11y tests catch only a subset of WCAG issues. Always inform the user that full compliance requires manual testing.

## Examples
**User:** "Add an accessibility check to our homepage test."
**Agent:** Reuses Playwright setup, asks to install `@axe-core/playwright`, injects axe into the homepage test, and asserts zero automated violations.