---
name: qa-visual-regression
description: Configures visual regression testing to detect pixel differences. Use when baselining UI components or changing global styles. Not for testing business logic.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA Visual Regression Testing

## Purpose
Ensures that code changes do not accidentally alter the visual appearance, layout, or typography of the application.

## When to Use
- When introducing global CSS changes.
- To baseline critical UI components (e.g., Design System library).
## When NOT to Use
- For testing business logic or API data.

## Prerequisites
- A visual testing framework (e.g., Playwright `toHaveScreenshot()`, Percy).

## Step-by-Step Instructions
1. **Define Scope:** Identify which pages or components need visual baselines.
2. **Handle Dynamic Data:** Mock dynamic elements (dates, animations) to prevent flaky snapshots.
3. **Write Snapshot Tests:** Configure the test to navigate to the page and capture the screenshot.
4. **Set Thresholds:** Define acceptable pixel difference thresholds (e.g., `maxDiffPixels`).
5. **Review Process:** Instruct the user on how to update baselines (`-u` flag).

## Validation Criteria
- Dynamic elements must be masked or mocked to ensure consistent screenshots.

## Safety Considerations
- Be mindful of OS-level rendering differences (snapshots generated on Mac may fail on Linux CI).

## Expected Output
A test script configured for visual comparison and instructions on managing baseline images.

## Examples
**User:** "Set up visual regression for our Button component in Playwright."
**Agent:** Creates a test that renders the Button in various states (hover, disabled) and asserts them against visual snapshots, masking any dynamic text.