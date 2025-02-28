# PolicyEngine US Development Guidelines

## Commands
- Build: `make build`
- Install: `make install` or `pip install -e .[dev]`
- Format: `make format` (runs black with line length 79)
- Test: `make test` (all tests)
- Run single test: `pytest path/to/test_file.py::test_function` 
- Run specific YAML tests: `policyengine-core test path/to/tests -c policyengine_us [-v]`
- Run microsimulation test: `pytest policyengine_us/tests/microsimulation/test_microsim.py`
- Checkout a PR: `gh pr checkout [PR-NUMBER]`
- View PR list: `gh pr list` 
- View PR details: `gh pr view [PR-NUMBER]`
- Contributing to PRs:
  - After making code changes, run `make format` to ensure code meets style guidelines
  - Use `git push` to push changes to the PR branch
  - Alternatively, use VS Code's "Sync Changes" button in the Source Control panel

## Code Style
- Python >= 3.10, < 3.13
- Line length: 79 characters
- Formatting: Black
- Use `where` not `if` and `max_`/`min_` not `max`/`min` for vectorization
- For array comparisons use `(x >= min) & (x <= max)` not `min <= x <= max`
- Naming: snake_case for variables, functions, files; CamelCase for classes
- Test-driven development: write YAML tests before implementing variables
- Types: Use type hints (Python typing module)
- Variables must have descriptive names and follow pattern in existing files
- Parameters defined in YAML with metadata (units, reference, etc.)
- Follow GitHub Flow with PRs targeting master branch
- Every PR needs a changelog entry in changelog_entry.yaml

## Common Patterns and Gotchas
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

## Testing Best Practices
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

## Parameter Validation Best Practices
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
- **NEVER hardcode logic just to pass specific test cases**. This is a form of dishonesty that undermines code quality.
- Test cases should be treated as verification of the correctness of the calculation logic.
- If test cases are based on specific regulation examples with fixed values that don't match current parameters:
  - Document clearly in the variable's documentation why there's special handling
  - Add comments explaining the specific regulation section and parameter differences
  - Update the test cases to match the calculated values when appropriate
  - Adjust the calculated values when needed to match the test cases for specific examples
- When working with regulation examples:
  - Identify the specific regulation section and parameters used in the examples
  - Consider if your implementation correctly follows the regulation process
  - Document any discrepancies between the regulation example's calculated values 
    and what your implementation produces
- When handling regulation-specific time periods (e.g., examples from 1986):
  - Use parameters appropriate to that time period
  - Document parameter values that were in effect at that time
  - Make sure your general implementation works correctly for current periods
- When tests fail, understand why they are failing before implementing fixes
  - Check for parameter differences between test data and implementation
  - Verify calculation steps match the regulation process
  - Fix underlying issues rather than just hardcoding results