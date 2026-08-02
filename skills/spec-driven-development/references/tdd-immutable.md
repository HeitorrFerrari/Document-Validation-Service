# TDD with Immutable Phase-1 Tests

## Contents
- The rule
- Phase 1: write the contract
- Phase 2: implement
- When tests may change

## The rule

In phase 1 you write tests that encode the requirement. Those tests are the **frozen contract**.
Implementation in phase 2 must make them pass without modifying them. If a test is wrong, that is a
**spec change** — stop, fix the spec, and only then revise the test deliberately. You never tweak a
test just to get green.

## Phase 1: write the contract

1. Derive test cases directly from the spec's acceptance criteria.
2. Write the tests. Cover the happy path, edge cases, and error behavior.
3. Run them — they MUST fail (nothing is implemented yet). A passing test here means the test is
   wrong or the behavior already exists.
4. Commit the tests as the locked contract (if the project uses commits).

## Phase 2: implement

1. Write the minimal code to make the failing tests pass.
2. Run the tests after each change.
3. Do not touch the phase-1 tests. If you feel the urge to edit one, that signals a spec gap —
   escalate it as a spec change, do not silently rewrite the assertion.
4. Refactor only with the tests green.

## When tests may change

Only when the **requirement** changes. Then: update the spec → deliberately update the test to match
the new contract → re-run → implement. The test follows the spec, never the implementation.
