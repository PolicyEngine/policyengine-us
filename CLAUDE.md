# PolicyEngine US - Development Guide

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
  - Alternatively, use VS Code's "Sync Changes" button in the Source Control panel

## Code Style Guidelines
- **Imports**: Use absolute imports from policyengine_us.model_api for Variables
- **Formatting**: Line length 79 characters; use Black for formatting
- **Types**: Use type hints; import ArrayLike from numpy.typing
- **Variable Naming**: Use snake_case for variable names and function names; use UPPER_CASE for constants
- **Error Handling**: Use np.divide with out/where parameters to avoid divide-by-zero errors
- **Documentation**: Add docstrings to classes and functions; include description, parameters, returns
- **Parameter Access**: Always use `p = parameters(period).gov.<program>` pattern and call parameters as `p.*` to make parameter tree origin clear
- **Constants**: Use UPPERCASE only for constants defined in code, not for parameters from the parameter tree
- **Income Combination**: Use `add(person, period, ["income1", "income2"])` instead of manual addition for combining income sources
- **Negative Values**: Use `max_(value, 0)` to clip negative values to zero (prevents counterintuitive behavior in economic models)

## Additional Guidelines
- Python >= 3.10, < 3.13
- Use `where` not `if` and `max_`/`min_` not `max`/`min` for vectorization
- For array comparisons use `(x >= min) & (x <= max)` not `min <= x <= max`
- Test-driven development: write YAML tests before implementing variables
- Variables must have descriptive names and follow pattern in existing files
- Parameters defined in YAML with metadata (units, reference, etc.)
- Follow GitHub Flow with PRs targeting master branch
- Every PR needs a changelog entry in changelog_entry.yaml

## Common Patterns and Gotchas
- **ALWAYS run `make format` before every commit** - this is mandatory and ensures consistent code style
- Unit tests with scalar values can pass while vectorized microsimulation fails
- When implementing a previously empty variable, be sure to check for dependent formulas
- When using `defined_for`, ensure it's tested in microsimulation context
- Be careful with chained comparisons in formulas - they work with scalars but fail with arrays
- Prefer explicit vectorized comparison operators joined with `&` and `|`
- Avoid using `if` checks with `.any()` in variable formulas as they can prevent proper vectorization
- Use `p = parameters(period).gov.<program>` pattern for accessing parameter trees
- Break complex calculations into separate variables for better modularity and testing
- In YAML tests, use `[val1, val2]` array syntax instead of hyphenated lists for output values
- When updating test values, add detailed calculation steps in comments to document the derivation
- For scale parameters that return integers, avoid using `rate_unit: int` in metadata (use `/1` instead) due to parameter validation issues
- Parameter file naming matters: make sure variables reference the exact parameter file name 
- When refactoring from enum to numeric values, update all downstream dependencies consistently
- Prefer parameter-driven calculations over hardcoded logic in formulas when possible
- Use `bool` instead of `int` or `/1` in `rate_unit` for scale parameters when appropriate to avoid validation issues
- For categorization logic, create separate variables for each test (e.g., `is_school_age`) and use them in downstream variables
- When dynamically determining numeric groups/categories, calculate values rather than hardcoding them (e.g., `max_value + 1`)
- Structure parameter files to match program documentation and real-world rules to improve maintainability
- Program takeup is assigned during microdata construction, not simulation time
  - Changes to takeup parameters (SNAP, EITC, etc.) have no effect in the web app
  - These parameters should include `economy: false` in their metadata
- When accessing yearly variables from month-level formulas, use `period.this_year`
  - Example: `age = person("age", period.this_year)` to get the actual age, not age/12
  - This is critical for variables like age that are defined per YEAR
- When refactoring federal programs to state-specific implementations:
  - Keep shared federal components (eligibility rules, age limits, etc.) if they're from federal regulations (CFR/USC)
  - Check all dependencies before removing variables - use grep to find references
  - Create integration tests to verify the refactoring works correctly
- State programs should be self-contained with their own income calculations and eligibility rules
  - Use state-specific variable names (e.g., `il_tanf_countable_income` not `tanf_countable_income`)
  - This allows states to have different rules without affecting each other
- **Labor Supply Response & Negative Earnings**: When dealing with income sources that can be negative (especially self-employment), use `max_(earnings, 0)` to prevent sign flips in economic responses. Negative total earnings should result in zero labor supply responses, not negative responses.
- **Module Refactoring**: When splitting large variable files, create individual files for each variable with comprehensive unit tests. Follow existing patterns like CTC module structure.

## Testing Best Practices
- **Test File Naming**:
  - Name unit test files after the variable being tested (e.g., `household_income_decile.yaml`)
  - Use `integration.yaml` for integration tests that test multiple variables together
  - Do not use any other naming patterns for test files

- **Test Formatting**:
  - **ALWAYS use underscore thousands separators** in numeric values (e.g., `1_000`, `50_000`, not `1000`, `50000`)
  - This applies to all numeric values in YAML tests including income, weights, thresholds, etc.

- **Unit Tests**: 
  - Create tests in `variable.yaml` that test only the direct inputs to `variable.py`
  - Unit tests should focus on validating a single variable's logic in isolation
  - Use simple inputs that test specific edge cases and logic branches
  - Variables higher in the dependency chain should stub their inputs directly
  - Each test should verify one specific behavior or case

- **Integration Tests**:
  - Place integration tests in `integration.yaml` within the relevant module directory
  - Integration tests verify the entire calculation pipeline works together
  - Test real-world scenarios with multiple people and complex household structures
  - Validate intermediate values along with final outputs
  - Include edge cases that test interactions between different parts of the system

## Parameter Structure Best Practices
- Cross-check parameter values against authoritative external sources (gov websites, calculators)
- Document the source, publication date, and effective dates in parameter metadata
- Include both title and href for references to maintain traceability
- Use multiple sources to validate complex parameters (e.g., tax brackets, benefit amounts)
- For annually updated values, document the adjustment methodology and inflation indices
- Test parameter values with real-world examples through YAML tests
- Be especially careful with multiplicative factors, which can significantly magnify errors
- Consider interactions between parameters when updating values
- When updating parameters, verify both individual values and downstream impacts
- Use descriptive changelog entries that reference authoritative sources for updates

## Regulatory Compliance Best Practices
- Always cite specific regulation sections in variable reference and documentation
- When implementing complex benefit calculations, clearly document the step-by-step process based on regulations
- Follow the exact order of operations specified in regulations (e.g., which exclusions apply first)
- Create dedicated unit tests for each step of complex benefit calculations
- Implement integration tests that verify the entire benefit calculation pipeline
- Add detailed comments that reference specific regulatory paragraphs or sections
- Create README documentation for complex modules or benefit programs
- For income tests or phaseouts, pay special attention to threshold values and differential calculations
- Verify behavior at edge cases (income just below/above thresholds, exact boundary conditions)
- Consider real-world examples to validate implementation, including official calculators or published examples

## Code Integrity and Test Data Handling
- **⚠️ ABSOLUTELY NEVER HARDCODE LOGIC JUST TO PASS SPECIFIC TEST CASES ⚠️** 
  - This is a serious form of dishonesty that undermines code quality and model integrity
  - It creates technical debt and maintenance nightmares
  - It destroys the ability to trust results and undermines the entire purpose of tests
  - NEVER add conditional logic that returns fixed values for specific input combinations
  - NEVER use period.start.year or other conditional checks to return hardcoded values for test cases
  - If you're tempted to hardcode values to make tests pass, you MUST fix the underlying issue instead
  
- Test cases should be treated as verification of the correctness of the calculation logic.

- If tests fail:
  1. FIRST understand WHY they are failing:
     - Is there a legitimate bug in the implementation?
     - Is there a misunderstanding of the regulations/policy?
     - Are the test expectations incorrect or outdated?
  2. Fix the ACTUAL ROOT CAUSE, not the symptom:
     - If the implementation is wrong, fix the formula/algorithm
     - If the test expectations are wrong, update the test expectations
     - If parameters have changed, document this and update accordingly

- When dealing with regulatory examples:
  - Use period-appropriate parameter values (e.g., for 1986 examples, use 1986 parameter values)
  - If you need special handling for an example year, make the algorithm work correctly for that year's parameters
  - Document any special time-period specific logic in BOTH code comments and variable documentation
  - Always ensure your implementation follows the general rules and principles for all time periods
  - Focus on preserving the calculation PROCESS rather than just matching specific OUTCOMES

- Never sacrifice correctness and maintainability for passing tests. It is better to have a failing test with a clear explanation than a "passing" test with incorrect implementation.

## Parameter Validation Gotchas
- When using `breakdown` metadata in parameters, avoid using variable references for integer values. Instead use Python expressions like `range(1, 5)`.
- The parameter validation system in policyengine-core has issues with certain parameter structures:
  - Using boolean keys (`True`/`False`) as parameter names can cause validation errors
  - Using integer output variables in breakdown metadata can cause parameter validation errors
  - If you encounter `UnboundLocalError: cannot access local variable 'possible_values'`, it's likely due to parameter validation issues
- To fix parameter validation issues:
  - Split complex parameters into separate, simpler parameter files
  - Use string names instead of boolean keys (e.g., `"eligible"` instead of `True`)
  - Use Python expressions like `range()` instead of variable references for enumerated values
  - Use breakdown patterns that match existing working examples in the codebase
  - See [GitHub issue #346](https://github.com/PolicyEngine/policyengine-core/issues/346) for more details

## Entity Structures and Relationships
- **Marital Units**: 
  - Include exactly 1 person (if unmarried) or 2 people (if married)
  - Do NOT include children or dependents
  - Defined in entities.py as "An unmarried person, or a married and co-habiting couple"
  - Used for calculations where spousal relationships matter (like SSI)
  - `marital_unit.nb_persons()` will return 1 or 2, never more

- **SSI Income Attribution**:
  - For married couples where both are SSI-eligible:
    - Combined income is attributed to each spouse via `ssi_marital_earned_income` and `ssi_marital_unearned_income`
    - These variables use `ssi_marital_both_eligible` to determine if combined income should be used
    - When both eligible, each spouse receives the combined household income for SSI calculations
  
- **SSI Spousal Deeming**:
  - Only applies when one spouse is eligible and the other is ineligible
  - If both are eligible, spousal deeming doesn't apply; instead income is combined through marital income variables

- **Debugging Entity Relationships**:
  - When checking entity totals or sums, be aware of which entity level you're operating at
  - For variables that need to sum across units, use `entity.sum(variable)`
  - Use `entity.nb_persons()` to count people in an entity
