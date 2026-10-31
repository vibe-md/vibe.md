---
name: test-first-react
description: Enforces Test-First (TDD) workflow for React components using React Testing Library. Use when building or changing React UI, components, forms, or pages. Always write tests before implementation code. When tests fail, stop and discuss with the user whether to fix the code or update the tests.
---

# Test-First React

## When to Use

Use this skill whenever the user asks to:
- Build a new React component, page, form, or feature
- Change existing React UI or behavior
- Fix a bug in React code
- Add or improve React functionality

Do **not** jump straight into writing component code.

## Core Rules (Must Follow)

1. **Tests come first**  
   Never write or change implementation code before tests exist and are approved.

2. **Stop on failure**  
   If any test fails after writing or changing code, **stop immediately**. Do not auto-fix. Open a discussion with the user.

3. **Discuss, don't assume**  
   When a test fails, present clear options and wait for the user's decision.

## Workflow

### Step 1 – Understand the requirement
- Restate what the user wants in simple terms.
- Ask clarifying questions if the expected behavior is unclear.

### Step 2 – Propose tests first
Write the tests **before** any component code.

Prefer React Testing Library best practices:
- Test user-visible behavior, not implementation details
- Use `screen`, `userEvent`, and queries like `getByRole`, `getByLabelText`, `getByText`
- Avoid testing internal state, class names, or component structure unless necessary

Present the tests to the user and ask for approval before continuing.

### Step 3 – Implement only after approval
Only after the user approves the tests:
- Write the minimal React code needed to make the tests pass
- Keep the implementation simple and focused

### Step 4 – Run the tests
After writing the code, run the relevant tests.

### Step 5 – Handle failures (Critical)
If any test fails:

1. **Stop**. Do not change code or tests yet.
2. Show the failing test(s) and the error clearly.
3. Present the user with these options:

   **Option A** – The test is correct → Fix the implementation code  
   **Option B** – The test is wrong or outdated → Update the test  
   **Option C** – The requirement changed → Update both tests and code  
   **Option D** – Something else (let the user explain)

4. Wait for the user's explicit choice before making any changes.

## Preferred Testing Stack

- React Testing Library
- Jest or Vitest
- `@testing-library/user-event`
- `@testing-library/jest-dom`

## Good Test Style (Examples of what to aim for)

```jsx
// Good – tests what the user sees and does
test('shows error when submitting empty form', async () => {
  render(<LoginForm />);
  await userEvent.click(screen.getByRole('button', { name: /login/i }));
  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
});