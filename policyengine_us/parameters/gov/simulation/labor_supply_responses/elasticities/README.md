# Labor Supply Response Elasticities

This directory contains parameters for labor supply response elasticities used in behavioral microsimulation analysis.

## Overview

Labor supply elasticities measure how individuals adjust their work behavior in response to changes in economic incentives:

- **Substitution elasticity**: How labor supply responds to changes in the effective marginal wage rate (after-tax wage)
- **Income elasticity**: How labor supply responds to changes in disposable income

## Age Heterogeneity: The Multiplier Approach

Both elasticity types support age-based heterogeneity through an **age multiplier** that scales base elasticities for individuals aged 65 and over. This approach is based on empirical research showing that older workers have higher labor supply elasticities than working-age adults.

### Research Findings

- **French (2005)**: Elasticities 3.0x-3.25x higher for age 60 vs age 40 workers
- **CBO Working Papers (2012-12, 2012-13)**: Frisch elasticity ranges from 0.27 to 0.53 (central: 0.40) for working-age adults
- **General pattern**: Retirement-age individuals (62-70) have particularly high elasticities, especially on the extensive margin (whether to work at all)

### Why a Multiplier Approach?

The multiplier approach was chosen over separate age-specific parameters because:
1. **Evidence-based**: Literature consistently shows older workers are more elastic, but doesn't provide income-decile-specific multipliers
2. **Parsimony**: 13 total parameters instead of 44 (11 base elasticities + 2 age multipliers)
3. **Transparency**: Users can easily understand and adjust one multiplier value
4. **Flexibility**: Multiplier can range from 1.0 (no age effect) to 3.0+ (French 2005 finding)

## Substitution Elasticity Structure

The substitution elasticity uses a two-step calculation:

### Step 1: Base Elasticity (by position and decile)

Base elasticities vary by:
1. **Position**: primary earner vs secondary earner within tax unit
2. **Decile**: 10 income deciles (for primary earners only)

This creates 11 base elasticity parameters:
- 10 for primary earners by decile
- 1 for secondary earners (all deciles)

### Step 2: Age Multiplier

For individuals aged 65 and over, the base elasticity is multiplied by `age_multiplier_65_and_over`.

**Formula**:
- If age < 65: `elasticity = base_elasticity`
- If age >= 65: `elasticity = base_elasticity × age_multiplier_65_and_over`

### Global Override

The `all` parameter overrides all base elasticities and age multipliers if set to non-zero.

## Income Elasticity Structure

The income elasticity uses a simpler two-parameter structure:

1. **Base elasticity**: Applied to all working-age individuals (under 65)
2. **Age multiplier**: Applied to individuals 65 and over

**Formula**:
- If age < 65: `elasticity = base`
- If age >= 65: `elasticity = base × age_multiplier_65_and_over`

The `all` parameter overrides base and multiplier if set to non-zero.

## Default Values

- All base elasticities default to 0 (no behavioral response)
- Age multipliers default to 2.0 (conservative estimate based on literature)
- Users must explicitly set base elasticity values to enable behavioral responses

## Usage Examples

### Example 1: No behavioral response (default)
```yaml
substitution:
  by_position_and_decile:
    primary:
      1: 0
      2: 0
      # ... all zeros
    secondary: 0
  age_multiplier_65_and_over: 2.0  # Doesn't matter since base is 0

income:
  base: 0
  age_multiplier_65_and_over: 2.0  # Doesn't matter since base is 0
```

Result: Everyone has zero elasticity regardless of age.

### Example 2: Same elasticity for all ages
```yaml
substitution:
  by_position_and_decile:
    primary:
      1: 0.31  # CBO-style values
      2: 0.27
      # ... other deciles
    secondary: 0.40
  age_multiplier_65_and_over: 1.0  # No age effect

income:
  base: -0.04
  age_multiplier_65_and_over: 1.0  # No age effect
```

Result: Same elasticity for everyone regardless of age.

### Example 3: Higher elasticity for elderly (RECOMMENDED)
```yaml
substitution:
  by_position_and_decile:
    primary:
      1: 0.31
      2: 0.27
      # ... other deciles
    secondary: 0.40
  age_multiplier_65_and_over: 2.0  # Conservative estimate

income:
  base: -0.04
  age_multiplier_65_and_over: 2.0
```

Result:
- Age 40, primary earner, decile 1: elasticity = 0.31
- Age 70, primary earner, decile 1: elasticity = 0.31 × 2.0 = 0.62
- Age 40: income elasticity = -0.04
- Age 70: income elasticity = -0.04 × 2.0 = -0.08

### Example 4: Aggressive multiplier based on French (2005)
```yaml
substitution:
  age_multiplier_65_and_over: 3.0  # Upper end of literature

income:
  base: -0.04
  age_multiplier_65_and_over: 3.0
```

Result:
- Age 70, primary earner, decile 1 (base 0.31): elasticity = 0.31 × 3.0 = 0.93
- Age 70: income elasticity = -0.04 × 3.0 = -0.12

## Multiplier Value Guidance

Based on literature review (see `age_heterogeneity_analysis.md`):

| Multiplier | Interpretation | Source |
|------------|----------------|--------|
| 1.0 | No age difference | Ignores evidence |
| 1.5 | Conservative | Lower end of estimates |
| 2.0 | **Recommended default** | Conservative but evidence-based |
| 2.5 | Moderate | Midpoint of French (2005) range |
| 3.0 | Aggressive | French (2005) finding for age 60 vs 40 |
| 3.25 | Upper bound | Upper end of French (2005) range |

**Note**: The exact multiplier value has uncertainty. We recommend starting with 2.0 and conducting sensitivity analysis with values in the 1.5-3.0 range.

## References

- [French (2005): "The Effects of Health, Wealth, and Wages on Labour Supply and Retirement Behaviour"](https://academic.oup.com/restud/article-abstract/72/2/395/1558553) - Review of Economic Studies 72(2): 395-427
- [CBO Working Paper 2012-12: "A Review of Recent Research on Labor Supply Elasticities"](https://www.cbo.gov/publication/43675) - McClelland & Mok
- [CBO Working Paper 2012-13: "Review of Estimates of the Frisch Elasticity of Labor Supply"](https://www.cbo.gov/publication/43676) - Reichling & Whalen

## Implementation Notes

- Age is determined from the `age` variable for the year (`period.this_year`)
- Age 65 is the cutoff: age < 65 uses base elasticity, age >= 65 applies multiplier
- Primary earner is defined as the highest earner within the tax unit
- Earnings deciles are determined using hardcoded markers (TODO: parametrize)
- Negative total earnings result in zero elasticity (using `max_(earnings, 0)`)
- Zero base elasticity remains zero even with multiplier (0 × multiplier = 0)

## Technical Details

### How Primary/Secondary Earner is Determined

Within each tax unit, the person with the highest total earnings (employment + self-employment) is designated as the primary earner. All other earners in the unit are secondary earners. This means:
- Single-person tax units: That person is always primary
- Multi-person tax units: Only the highest earner gets primary elasticity; others get zero (since secondary earner base elasticities default to 0)

### Earnings Decile Markers

Current hardcoded decile boundaries (TODO: parametrize):
- Decile 1: $0 - $14,000
- Decile 2: $14,000 - $28,000
- Decile 3: $28,000 - $39,000
- Decile 4: $39,000 - $50,000
- Decile 5: $50,000 - $61,000
- Decile 6: $61,000 - $76,000
- Decile 7: $76,000 - $97,000
- Decile 8: $97,000 - $138,000
- Decile 9: $138,000 - $1,726,000
- Decile 10: $1,726,000+

### Negative Earnings Handling

To prevent negative earnings from causing sign flips in economic responses, the code applies `max_(earnings, 0)` before calculating elasticities. This means:
- Positive net earnings: Normal elasticity calculation
- Negative net earnings: Treated as zero earnings, resulting in zero substitution elasticity
- Income elasticity still applies to individuals with negative earnings
