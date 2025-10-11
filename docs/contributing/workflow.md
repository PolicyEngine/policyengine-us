# Development Workflow

This guide covers the typical workflow for contributing to PolicyEngine US.

## GitHub Flow

We follow [GitHub Flow](https://guides.github.com/introduction/flow/):

1. **Fork & Clone** - Create your own copy of the repository
2. **Create Branch** - Make a feature branch for your changes
3. **Make Changes** - Implement your feature or fix
4. **Test Locally** - Run tests to ensure everything works
5. **Push to Fork** - Push your branch to your GitHub fork
6. **Open PR** - Create a pull request to the main repository
7. **Code Review** - Maintainers review and provide feedback
8. **Merge to master** - Once approved, changes are merged

## Step-by-Step Guide

### 1. Always Start with an Issue

**We follow an issue-first workflow**:
- Check existing [issues](https://github.com/PolicyEngine/policyengine-us/issues)
- If none exist, create one before starting work
- Comment on the issue to claim it
- For major changes (especially new programs), it's helpful to discuss your approach in the issue first

Good issues include:
- **Bug description** with reproduction steps
- **Feature request** with use case
- **New program implementation** with legislative references
- **Links to legislation** or government sources (e.g., tax forms, CFR citations)
- **Expected behavior** clearly described

For new programs, your issue should specify:
- Program name and jurisdiction (federal/state)
- Key eligibility rules and benefit calculations
- Links to authoritative sources (statutes, regulations, forms)
- Example calculations if available

### 2. Fork and Clone

```bash
# Fork via GitHub UI, then:
git clone https://github.com/YOUR_USERNAME/policyengine-us.git
cd policyengine-us
git remote add upstream https://github.com/PolicyEngine/policyengine-us.git
```

### 3. Create a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout master
git merge upstream/master

# Create your branch
git checkout -b fix-ctc-calculation
```

Branch naming conventions:
- `fix-{description}` for bug fixes
- `add-{description}` for new features
- `update-{description}` for updates
- `docs-{description}` for documentation

### 4. Make Your Changes

#### For New Variables

1. **Write tests first** (TDD approach):
```yaml
# policyengine_us/tests/policy/baseline/gov/states/ny/tax/income/test_ny_agi.yaml
- name: Basic NY AGI calculation
  period: 2024
  input:
    adjusted_gross_income: 50_000
  output:
    ny_agi: 50_000
```

2. **Create the variable**:
```python
# policyengine_us/variables/gov/states/ny/tax/income/ny_agi.py
from policyengine_us.model_api import *

class ny_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/forms/income_cur_forms/it201i.pdf"
    
    def formula(tax_unit, period, parameters):
        return tax_unit("adjusted_gross_income", period)
```

#### For Parameter Updates

1. **Update YAML parameter files**:
```yaml
# policyengine_us/parameters/gov/states/ny/tax/income/rates.yaml
description: New York income tax rates
metadata:
  unit: /1
  reference:
    - title: NY Tax Law § 601
      href: https://www.nysenate.gov/legislation/laws/TAX/601
values:
  2024-01-01: 0.04
  2023-01-01: 0.035
```

2. **Add tests for new values**

### 5. Test Your Changes

```bash
# Format code (runs black + linecheck)
make format

# Run all tests
make test

# Run specific tests
pytest policyengine_us/tests/policy/baseline/gov/states/ny/ -v

# Run YAML tests
policyengine-core test policyengine_us/tests/policy/baseline/gov/states/ny/ -c policyengine_us
```

### 6. Update Changelog

Create `changelog_entry.yaml`:
```yaml
- bump: patch
  changes:
    added:
      - NY AGI variable for state tax calculations
```

### 7. Commit and Push

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add NY AGI variable for state tax calculations

- Implement ny_agi variable based on federal AGI
- Add comprehensive tests
- Reference NY Tax Law § 601"

# Push to your fork
git push origin fix-ctc-calculation
```

### 8. Open Pull Request

1. Go to your fork on GitHub
2. Click "Pull request"
3. **CRITICAL**: Link to the issue using [GitHub's linking keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue):
   - Use `Fixes #123` to auto-close the issue when PR merges
   - Use `Addresses #123` if it partially addresses the issue
   - Use `Refs #123` for related issues

Example PR description:
```markdown
## Summary
Adds New York Adjusted Gross Income (AGI) calculation for state tax computations.

## Changes
- New variable: `ny_agi` 
- Tests for various income scenarios
- Documentation with legislative references

## Testing
- All existing tests pass
- New tests cover edge cases
- Manually verified against NY tax calculator

Fixes #456
```

**Tips for success**:
- Always link your PR to an issue for better tracking
- For major changes or new programs, discuss your approach in the issue first
- Stay aligned with what was discussed in the issue to avoid rework

### 9. Code Review Process

During review:
- Respond to feedback promptly
- Make requested changes
- Push new commits (don't force-push)
- Re-request review when ready

Common review feedback:
- Missing tests
- Incorrect formatting (run `make format`)
- Missing references
- Logic errors

### 10. After Merge

```bash
# Update your local master
git checkout master
git fetch upstream
git merge upstream/master

# Delete your feature branch
git branch -d fix-ctc-calculation
git push origin --delete fix-ctc-calculation
```

## Best Practices

### Commit Messages

Good commit messages:
- First line: concise summary (50 chars)
- Blank line
- Detailed explanation if needed
- Reference issues/PRs

```
Fix CTC phase-out calculation for joint filers

The previous implementation used single filer thresholds for all
filing statuses. This updates the logic to use the correct
thresholds based on filing status.

Fixes #789
```

### PR Etiquette

- Keep PRs focused and small
- One feature/fix per PR
- Include tests
- Update documentation
- Be responsive to feedback
- Don't force-push after review starts

### Working with Large Changes

For major features:
1. Discuss approach in issue first
2. Break into smaller PRs
3. Use feature flags if needed
4. Coordinate with maintainers

## Continuous Integration

All PRs must pass CI checks:
- Code formatting (Black)
- All tests passing
- Documentation builds
- Changelog entry present

Monitor CI status and fix any failures before requesting review.

## Tips for Success

1. **Start small** - Pick a simple issue first
2. **Ask questions** - We're here to help
3. **Test thoroughly** - Prevents back-and-forth
4. **Document well** - Future you will thank you
5. **Be patient** - Reviews take time