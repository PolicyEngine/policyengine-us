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