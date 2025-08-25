# PolicyEngine Implementation Standards

This document contains the shared standards and guidelines that all PolicyEngine agents must follow, particularly the Rules Engineer and Reviewer agents.

## Source Documentation Requirements

### Hierarchy of Authority
Sources must be cited in this order of preference:
1. **Statutes/Laws** (e.g., 42 USC § 1382)
2. **Regulations** (e.g., 7 CFR 273.9)
3. **Official Program Manuals**
4. **Government websites** (only as last resort)

### Citation Requirements
Every parameter and variable MUST have:
- Direct citation to authoritative source
- Specific section/subsection reference
- Valid URL that links to the exact location
- Effective date clearly specified

### Common Citation Issues to Check
- ❌ Generic website links without specific sections
- ❌ "See manual" without page/section numbers
- ❌ Outdated regulations (check for amendments)
- ❌ Secondary sources when primary sources exist
- ✅ Direct links to specific CFR sections
- ✅ USC citations with subsection references
- ✅ Page numbers for PDF manuals

## Parameter Standards

### Metadata Requirements
```yaml
description: Federal minimum wage  # ACTIVE VOICE, no "The" prefix
values:
  2024-01-01: 7.25
metadata:
  unit: currency-USD
  period: hour
  reference:
    - title: 29 USC § 206(a)(1)  # Law first
      href: https://www.law.cornell.edu/uscode/text/29/206
    - title: DOL Minimum Wage  # Agency guidance second
      href: https://www.dol.gov/agencies/whd/minimum-wage
```

### Common Parameter Issues
- **Missing effective dates**: Every value change needs a date
- **Wrong units**: Ensure unit matches the value (e.g., currency-USD vs /1)
- **Passive voice in descriptions**: Use "Federal minimum wage" not "The federal minimum wage is"
- **Generic references**: Need specific statute/regulation sections

## Variable Standards

### Documentation Requirements
```python
class variable_name(Variable):
    value_type = float
    entity = Person
    label = "Clear, concise label"  # ACTIVE VOICE
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9"  # SPECIFIC section
    documentation = """
    Brief description of what this calculates.
    References specific regulation sections for each step.
    """
```

### Formula Requirements
- **Vectorization**: MUST use `where()`, `select()`, or boolean multiplication
- **No if-elif-else**: These don't work with arrays
- **Edge case handling**: Use `max_(0, value)` to prevent negative values
- **Clear variable names**: Use descriptive names that match regulations

## Testing Standards

### Integration Test Requirements
```yaml
- name: Descriptive test name matching scenario
  period: 2024
  input:
    # Complete inputs needed
  output:
    # Expected values with comments showing calculation
    # Per 7 CFR 273.9: $1,000 - $100 = $900
    variable_name: 900
```

### Test Documentation
Every non-trivial test should include:
- Reference to regulation section
- Step-by-step calculation
- Explanation of why this case matters

## Common Implementation Pitfalls

### Critical Code Issues
1. **Non-vectorized code (if-elif-else)**
   - ❌ NEVER use if-elif-else with household/person data (will crash with arrays)
   - ✅ OK to use if-else for parameter-only conditions:
     ```python
     # ✅ OK - parameter condition only
     if p.program.enabled:
         rate = p.program.rate
     else:
         rate = 0
     
     # ❌ WRONG - depends on household data
     if person("age") > 65:
         benefit = amount
     ```
   - For household data, must use `where()`, `select()`, or boolean multiplication
   
2. **Hardcoded values in formulas**
   - ❌ `if income > 50000:` (hardcoded threshold)
   - ✅ `if income > p.income_threshold` (parameter)
   
3. **Missing `defined_for` when needed**
   - Variables that only apply to certain groups need `defined_for`
   - Example: `defined_for = "is_ssi_eligible"`
   
4. **Not using `adds` for aggregation**
   - When summing multiple sources, use `adds` in metadata
   - Example: `adds = ["gov.irs.income.wages", "gov.irs.income.interest"]`

### YAML Test Issues
1. **Missing thousands separators**
   - ❌ `income: 50000`
   - ✅ `income: 50_000`
   
2. **Incorrect period format**
   - ❌ `period: 2024-01-01`
   - ✅ `period: 2024` (for annual)
   - ✅ `period: 2024-01` (for monthly)

## Common Issues to Flag

### Documentation Issues
1. **Parameter doesn't match cited source**
   - Check actual values in statute/regulation
   - Verify effective dates
   - Look for amendments

2. **Missing primary sources**
   - Parameters citing only websites
   - No statute/regulation reference
   - Using summaries instead of law text

3. **Calculation doesn't follow regulation order**
   - Regulations often specify exact order of operations
   - Deductions/exclusions must be applied in correct sequence

### Style Issues
1. **Description style**
   - ❌ "The amount of SNAP benefits"
   - ✅ "SNAP benefits"
   - ❌ "This variable calculates..."
   - ✅ "Amount of..."

2. **Variable naming**
   - Should match program terminology
   - Use program's official abbreviations
   - Consistent with existing variables

3. **Test clarity**
   - Missing calculation explanations
   - Unclear why expected value is correct
   - No reference to regulation

## Verification Checklist

### For Rules Engineer (During Implementation)
- [ ] Every parameter cites primary source
- [ ] All formulas follow regulation sequence
- [ ] Variables use active voice labels
- [ ] Code is fully vectorized
- [ ] Edge cases handled (negatives, zeros)
- [ ] Unit tests cover basic cases

### For Reviewer (During Review)
- [ ] Parameter values match source documents exactly
- [ ] Citations link to specific sections
- [ ] Calculations follow regulatory order
- [ ] All test expected values verified against regulations
- [ ] No hardcoded test-specific values
- [ ] Complete documentation trail

## Red Flags Requiring Immediate Attention

1. **Parameter value doesn't match source**: CRITICAL - affects real calculations
2. **If-elif-else in formula**: CRITICAL - will crash with arrays
3. **No primary source citation**: MAJOR - can't verify accuracy
4. **Wrong calculation order**: MAJOR - produces incorrect results
5. **Passive voice descriptions**: MINOR - but fix for consistency
6. **Missing test documentation**: MINOR - but important for maintenance

## References for Common Programs

### Federal Programs
- **SSI**: 42 USC § 1381-1383, 20 CFR Parts 416
- **SNAP**: 7 USC § 2011-2036, 7 CFR Part 273
- **TANF**: 42 USC § 601-619, 45 CFR Part 260-265
- **Medicaid**: 42 USC § 1396, 42 CFR Part 430-456

### State Programs
Always check:
- State statutes (usually available on state legislature website)
- State administrative code/regulations
- Official program manuals from state agencies

## Remember

The goal is to ensure every calculation in PolicyEngine can be traced back to authoritative law or regulation. When in doubt:
1. Find the primary source
2. Cite the specific section
3. Document the derivation
4. Test with real examples from regulations