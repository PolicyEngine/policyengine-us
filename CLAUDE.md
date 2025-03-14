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

  ## Task Instructions: Updating Oregon State Tax Code Parameters

We have a text file named **`oregon.txt`** containing updated information about Oregon’s state tax parameters. Your job is to:

1. **Identify each parameter** in our Oregon parameter YAML files that corresponds to a parameter listed in **`oregon.txt`**.  
2. **Compare the 2024 values** to the existing 2023 values in our codebase.

   - If the 2024 value is **different** from the 2023 value, **append** the 2024 value as a **new entry**.  
     ```yaml
     2022-01-01: 7_500
     2023-01-01: 8_100
     2024-01-01: 8_200  # <--- newly added if 2024 changed
     ```
   - If the **2023 value is the same** as the 2024 value, **do not** add a new entry; keep the 2023 date/value pair as the last entry.  

3. **Add the updated reference** for 2024, **whether or not** the value changed. 

   For references, use the following format (with the correct page number from `oregon.txt`):
   ```yaml
   - title: 2023 Oregon Income Tax Form OR-40 Instructions
     href: https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2023.pdf#page=[PAGE_NUMBER]

  ### Page References
Page numbers appear in `oregon.txt` as `--- Page X ---`. Make sure you 
include the exact page where the relevant information is found.

### Change Alerts
- **Alert** if any parameter values have changed.
- After updating, **note which parameters received new 2024 values**.

### Additional Notes
- **Line length**: Keep each line ≤ 79 characters when editing the YAML files.
- **Vectorization**: Remains relevant if we add or modify formulas downstream.

### Testing
- After changes, **run `make test`** to ensure no regressions.
- Consider adding or adjusting **YAML tests** if the new parameters introduce 
  new conditions or thresholds.

### Changelog
- Add a note in `changelog_entry.yaml` summarizing the Oregon parameter 
  updates.
- Reference the source (`oregon.txt` and the official PDF).