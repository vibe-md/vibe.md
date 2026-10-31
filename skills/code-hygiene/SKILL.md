---
name: code-hygiene
description: Keeps AI-written code real, used, and written once. Checks for an existing helper before creating a new one, verifies every third-party API against the installed version before using it, and cleans up code the change left orphaned. Use when adding functions, hooks, components, or utilities; when calling or upgrading a third-party package or editing framework config; after finishing a feature or abandoning an approach; or when an error says something is undefined, not a function, not exported, or an unknown option.
license: MIT
compatibility: Works in any language. Command examples target JavaScript and TypeScript projects; other ecosystems are covered in references/ecosystems.md.
metadata:
  collection: vibe.md
  categories: Productivity, AI / Agents, Frontend
  maintainers: arjar88
  title: Code Hygiene
---

# Code hygiene

**Real. Used. Once.**

## Purpose

Coding agents leave three kinds of mess behind:

| Problem | What it looks like | Why agents cause it |
| --- | --- | --- |
| Duplicates | A third `formatDate`, a second `useDebounce`, a new `Button` beside the existing one | The agent writes before it searches |
| Phantom APIs | A hook, prop, or config key that does not exist in the installed version | The agent codes from memory of an older or different library |
| Dead code | Unused files, exports, and packages from abandoned attempts | The agent changes direction and never cleans up |

This skill handles all three in the order they happen during a task:

```text
Before writing  ->  Search: does this already exist?             (Once)
While writing   ->  Verify: does this API really exist?          (Real)
After writing   ->  Sweep: did this change leave anything unused? (Used)
```

## When to Use

- About to create a new function, hook, component, type, constant, or utility.
- Writing code that calls a third-party package, adding or upgrading a dependency, or editing framework config (`next.config.*`, `vite.config.*`, `metro.config.js`, `babel.config.js`, `tsconfig.json`, `tailwind.config.*`, `eslint.config.*`, `app.json`, and similar).
- An error reads `is not a function`, `is not exported from`, `Cannot find module`, `Unknown option`, `Unrecognized key`, or `Property does not exist on type`.
- A feature is finished, or an approach was abandoned partway through.
- The user asks to clean up unused code, find duplicates, or check that an API exists.

Do not use this skill to restyle or reformat code, to consolidate duplicates the current task did not create (report them instead), or to upgrade dependencies for their own sake.

## Prerequisites

- Read access to the project, including its installed dependencies (`node_modules` or the ecosystem's equivalent). If dependencies are not installed, ask the user before running an install.
- Optional: `npx` access to `knip` and `depcheck` for the cleanup step. Ask before installing either as a project dependency.

## Instructions

### Once: search before creating

1. Before creating anything new, search the codebase by likely names **and** by behavior. Agents and people rarely pick the same name.

   ```bash
   grep -rniE "formatDate|formatTime|dateFormat" src
   grep -rniE "debounce|throttle" src
   grep -rniE "Intl\.DateTimeFormat|toLocaleDateString" src
   ```

   Look in the usual homes for shared code (`utils/`, `lib/`, `helpers/`, `hooks/`, `shared/`, `common/`, `components/ui/`), in the project's design system or UI kit, and in existing type definitions.
2. Check installed packages. If `date-fns`, `lodash`, `zod`, `clsx`, or similar is already a dependency, use it before writing a custom version.
3. Decide, and say which you chose:
   - **Exact match:** import and reuse it. Never copy and tweak it.
   - **Close match:** extend it with a small, backward-compatible change (a parameter or variant). If the change alters behavior for other callers, list those callers and ask first.
   - **A package covers it:** use the package.
   - **Nothing exists:** create it in the shared location the project already uses, not inline in a screen or page file.
4. If you find duplicates that already existed before this task, report them. Do not consolidate them without approval; that is a separate refactor.

### Real: verify every third-party API

The rule: **never use a third-party API you have not verified against the installed version.** Memory is a lead; the installed package is the proof.

5. Verify every third-party import, component prop, options-object field, config key, CLI flag, and library-read environment variable added in this task. Skip language built-ins, basic long-stable core APIs (`useState`, `useEffect`), and code inside the repository, which you read directly.
6. Get the installed version, not the range in `package.json`, and note the major version. Most phantom APIs come from crossing a major boundary.

   ```bash
   npm ls <pkg>            # or: pnpm why <pkg> / yarn why <pkg>
   grep '"version"' node_modules/<pkg>/package.json
   ```

7. Check sources of truth in this order, stopping at the first conclusive answer:
   1. Installed type definitions: `grep -rn "<symbol>" node_modules/<pkg> --include=*.d.ts`
   2. The `exports` field of `node_modules/<pkg>/package.json`, for legal import paths
   3. `CHANGELOG.md` and `README.md` inside `node_modules/<pkg>`, for renames and removals
   4. Official documentation for that exact major version (doc sites usually default to the latest)
   5. Memory, as a guess to check, never as proof

   For props and options, confirm the name, the type, and whether it is required. If the API exists but differs from what you remember, the installed version wins: look for a rename, a move to another import path or package, a deprecation, a new signature, or changed defaults.
8. Let the compiler confirm with the cheapest available check: `npx tsc --noEmit`, the project's lint script, then its build script. Config keys are often untyped and silently ignored when wrong, so a clean type check alone does not prove them; step 7 does.
9. If the API does not exist: stop, find the real equivalent in the installed version, and tell the user what you expected, what exists, and what you used. If there is no equivalent, offer the options (implement it locally, upgrade with the major version jump stated, or take another approach) and let the user choose.
10. Take extra care with recently rewritten libraries (routing, navigation, auth SDKs, ORMs, styling frameworks, bundler config, React Native and Expo) and look-alike pairs (Jest and Vitest, React Navigation and Expo Router, Prisma and Drizzle, Supabase JS v1 and v2). When one of the errors listed under When to Use appears, assume a phantom API and repeat step 7 before trying any other fix.

### Used: sweep what this task orphaned

11. When the task is finished, or an approach is abandoned, list what this task made unused: files and components from abandoned attempts, exports whose last caller was removed, imports and variables no longer read in edited files, packages installed for a dropped approach, leftover debug logging, temporary files, and commented-out blocks added during the task. Sweep the whole repository only when the user asks.
12. Use tools to find candidates, then verify each by hand. Tools report false positives.

    ```bash
    npx knip                # unused files, exports, and dependencies
    npx depcheck            # unused or missing dependencies
    ```

13. Before calling anything dead, search for its file name and symbol name across the repository, including config and native folders. Something can look unused yet still be live through file-based routing (`app/`, `pages/`, API routes), dynamic `import()` or `require()`, string-keyed registries, config files that reference it by path, a package's public exports consumed elsewhere in a monorepo, Storybook stories, test fixtures, `package.json` scripts, CI workflows, or side-effect imports such as `import './polyfills'`.
14. Propose first, delete second. List what you will remove and why, and wait for approval. The one exception: unused imports and variables in files you edited during this task may be removed directly. Remove packages with the package manager (`npm uninstall <pkg>`), never by editing `package.json` by hand. Run the type check, tests, and build afterwards.

### Never, without explicit approval

- Copy an existing function to tweak it instead of reusing or extending it.
- Install, upgrade, or downgrade a package to make an API exist.
- Hide a missing API with `as any`, `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, an invented `declare module`, optional chaining such as `lib.fn?.()`, or a `try`/`catch`.
- Delete files, exports, or packages outside the current task's footprint.

### Report

15. End the task with a short hygiene report, including only the sections that apply:

    ```text
    Code hygiene

    Reused (Once)
    - formatPrice -> src/utils/currency.ts (existing; no new helper created)

    Verified APIs (Real)
    | API                           | Installed                 | Status    | Source              |
    | useNavigate()                 | react-router-dom 6.26.2   | exists    | index.d.ts          |
    | <Image placeholderColor>      | expo-image 1.12.0         | not found | used `placeholder`  |

    Cleanup (Used)
    - Removed: unused imports in SearchBar.tsx
    - Proposed, awaiting approval: src/components/OldCarousel.tsx and react-native-snap-carousel

    Found, not changed
    - formatDate exists in both src/utils/date.ts and src/lib/format.ts

    Checks: tsc --noEmit passed, lint passed, build passed
    ```

    If a check could not run, say which and why. Do not call the task done without it.

For Python, Go, Rust, Ruby, Swift, and Android equivalents of these commands, see [ecosystem commands](references/ecosystems.md).

## Examples

**User:** "Add a debounced search input to the products page."

**Agent:** Searches for `debounce` and finds `src/hooks/useDebounce.ts` plus `lodash.debounce` in the dependencies. Reuses the hook instead of writing a new one, verifies the third-party input component's `onChangeText` prop in its installed type definitions, runs the type check, and reports "Reused: useDebounce" with no new helpers created.

**User:** "Navigate to the home screen after login."

**Agent:** Checks the installed `react-router-dom` (6.26.2), finds that `useHistory` is not exported in v6 by checking `index.d.ts`, and uses `useNavigate()` instead, saying why. The type check passes.

**User:** "Let's drop the custom carousel and use FlashList."

**Agent:** Switches to FlashList, then finds that `OldCarousel.tsx` and `react-native-snap-carousel` have no remaining references after checking routes, config, tests, and Storybook. It asks before removing them, uninstalls the package with the package manager once approved, and reruns the build.
