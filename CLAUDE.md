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
- When updating parameter values (e.g., premium data, tax thresholds), verify with external sources
- SLCSP (ACA premium) data should be verified against healthcare.gov or KFF calculator
- Age curve multipliers in ACA calculations significantly impact results (e.g., 1.6706 for age 40)
- Parameter files should include clear metadata about sources and last update dates