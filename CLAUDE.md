# PolicyEngine US - Development Guide

## ⚠️ MANDATORY FIRST ACTION

At the START of each session, ask the user:

"Would you like to load PolicyEngine development skills for this session?"

**Options to present:**
1. "Yes, load skills" (Recommended) - Load pattern skills for code quality
2. "No, skip" - Proceed without loading skills

**If Option 1 selected, load ALL of these:**
- /policyengine-code-style
- /policyengine-parameter-patterns
- /policyengine-period-patterns
- /policyengine-testing-patterns
- /policyengine-variable-patterns

---

## Build/Test/Lint Commands
```bash
# Install dependencies
make install
# Alternative installation
pip install -e .[dev]

# Format code
make format  # Runs black with line length 79 and fixes import ordering

# Run all tests
make test

# Run specific test file or directory
pytest policyengine_us/tests/path/to/test_file.py

# Run specific test function
pytest policyengine_us/tests/path/to/test_file.py::test_function_name

# Run specific YAML tests
policyengine-core test path/to/tests -c policyengine_us [-v]

# Run microsimulation test
pytest policyengine_us/tests/microsimulation/test_microsim.py

# Run YAML-specific tests
make test-yaml-structural
make test-yaml-no-structural

# Generate documentation
make documentation
```

## GitHub Workflow
- Checkout a PR: `gh pr checkout [PR-NUMBER]`
- View PR list: `gh pr list`
- View PR details: `gh pr view [PR-NUMBER]`
- Contributing to PRs:
  - **ALWAYS run `make format` before committing** - this ensures code meets style guidelines and is non-negotiable
  - Use `git push` to push changes to the PR branch

## Project Requirements
- Python >= 3.10, < 3.13
- Follow GitHub Flow with PRs targeting master branch
- Every PR needs a changelog entry in changelog_entry.yaml
- **ALWAYS run `make format` before every commit** - this is mandatory

## Project-Specific Gotchas
- Unit tests with scalar values can pass while vectorized microsimulation fails
- When implementing a previously empty variable, check for dependent formulas
- When using `defined_for`, ensure it's tested in microsimulation context
- For scale parameters that return integers, avoid using `rate_unit: int` in metadata (use `/1` instead)
- Use `bool` instead of `int` or `/1` in `rate_unit` for scale parameters when appropriate
- Program takeup is assigned during microdata construction, not simulation time
  - Changes to takeup parameters (SNAP, EITC, etc.) have no effect in the web app
  - These parameters should include `economy: false` in their metadata
- **Labor Supply Response & Negative Earnings**: Use `max_(earnings, 0)` to prevent sign flips. Negative total earnings should result in zero labor supply responses.

## State Program Patterns
- When refactoring federal programs to state-specific implementations:
  - Keep shared federal components if they're from federal regulations (CFR/USC)
  - Check all dependencies before removing variables - use grep to find references
  - Create integration tests to verify the refactoring works correctly
- State programs should be self-contained with their own income calculations and eligibility rules
  - Use state-specific variable names (e.g., `il_tanf_countable_income` not `tanf_countable_income`)

## Regulatory Compliance
- Always cite specific regulation sections in variable reference and documentation
- When implementing complex benefit calculations, document the step-by-step process based on regulations
- Follow the exact order of operations specified in regulations
- Verify behavior at edge cases (income just below/above thresholds, exact boundary conditions)
- Consider real-world examples to validate implementation, including official calculators

## Code Integrity
- **ABSOLUTELY NEVER HARDCODE LOGIC JUST TO PASS SPECIFIC TEST CASES**
  - NEVER add conditional logic that returns fixed values for specific input combinations
  - NEVER use period.start.year or other conditional checks to return hardcoded values for test cases
  - If tests fail, fix the ACTUAL ROOT CAUSE, not the symptom

- When dealing with regulatory examples:
  - Use period-appropriate parameter values
  - Document any special time-period specific logic in BOTH code comments and variable documentation
  - Focus on preserving the calculation PROCESS rather than just matching specific OUTCOMES

## Parameter Validation Gotchas
- When using `breakdown` metadata in parameters, avoid using variable references for integer values. Use Python expressions like `range(1, 5)`.
- The parameter validation system has issues with certain structures:
  - Using boolean keys (`True`/`False`) as parameter names can cause validation errors
  - Using integer output variables in breakdown metadata can cause errors
- To fix validation issues:
  - Split complex parameters into separate, simpler parameter files
  - Use string names instead of boolean keys
  - See [GitHub issue #346](https://github.com/PolicyEngine/policyengine-core/issues/346)

## Entity Structures
- **Marital Units**:
  - Include exactly 1 person (if unmarried) or 2 people (if married)
  - Do NOT include children or dependents
  - `marital_unit.nb_persons()` will return 1 or 2, never more

- **SSI Income Attribution**:
  - For married couples where both are SSI-eligible: combined income is attributed to each spouse via `ssi_marital_earned_income` and `ssi_marital_unearned_income`

- **SSI Spousal Deeming**:
  - Only applies when one spouse is eligible and the other is ineligible
