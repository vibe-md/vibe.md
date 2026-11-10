---
name: qa-accessibility-testing
description: Automates accessibility testing to ensure WCAG compliance. Use when auditing web pages for keyboard navigation and contrast. Not for backend non-UI services.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA Accessibility Testing

## Purpose
Validates that web applications are accessible to all users, verifying contrast, ARIA attributes, and keyboard navigation.

## When to Use
- When building new UI components or web pages.
- Auditing existing sites for WCAG violations.
## When NOT to Use
- For non-UI backend services.

## Prerequisites
- UI testing framework installed (e.g., Playwright with `@axe-core/playwright`).

## Step-by-Step Instructions
1. **Inject Axe:** Configure the test to inject `axe-core` into the page.
2. **Define Rulesets:** Specify which WCAG standards to test against (e.g., WCAG 2.1 AA).
3. **Scan Page:** Execute the accessibility scan on specific components or the whole page.
4. **Filter Violations:** Exclude known third-party violations if necessary.
5. **Report Output:** Format the findings into a clear list of violations.

## Validation Criteria
- The test must explicitly catch contrast issues, missing alt text, and invalid ARIA roles.

## Safety Considerations
- Automated a11y tests catch only ~30% of issues; remind the user that manual keyboard testing is still required.

## Expected Output
An automated script that runs an accessibility audit and a report structure for violations.

## Examples
**User:** "Add an accessibility check to our homepage test."
**Agent:** Integrates `@axe-core/playwright`, navigates to the homepage, analyzes the DOM, and adds an assertion `expect(accessibilityScanResults.violations).toEqual([])`.