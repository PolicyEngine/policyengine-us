# Labor Supply Response Elasticities

This directory contains parameters for labor supply response elasticities used in behavioral microsimulation analysis.

## Overview

Labor supply elasticities measure how individuals adjust their work behavior in response to changes in economic incentives:

- **Substitution elasticity**: How labor supply responds to changes in the effective marginal wage rate (after-tax wage)
- **Income elasticity**: How labor supply responds to changes in disposable income

## Age Heterogeneity

Both elasticity types support age-based heterogeneity, recognizing that older workers (65+) have different labor supply responses than younger workers:

- **Under 65**: Working-age population
- **65 and over**: Retirement-age population

### Research Findings

Congressional Budget Office research shows:
- Older workers generally adjust their hours more than younger workers in response to wage changes
- Retirement-age individuals (62-70) have particularly high own-wage elasticities, especially on the extensive margin (whether to work at all)
- The Frisch elasticity ranges from 0.27 to 0.53 (central estimate: 0.40)

## Substitution Elasticity Structure

The substitution elasticity varies by three dimensions:

1. **Age**: under_65 vs 65_and_over
2. **Position**: primary earner vs secondary earner within tax unit
3. **Decile**: 10 income deciles (for primary earners only)

This creates 22 distinct elasticity values per age group (44 total):
- 10 for primary earners by decile (under 65)
- 1 for secondary earners (under 65)
- 10 for primary earners by decile (65 and over)
- 1 for secondary earners (65 and over)

### Global Override

The `all` parameter overrides all age/position/decile-specific values if set to non-zero.

## Income Elasticity Structure

The income elasticity varies by age only:
- `under_65`: Income elasticity for working-age population
- `65_and_over`: Income elasticity for retirement-age population

The `all` parameter overrides age-specific values if set to non-zero.

## Default Values

All elasticities default to 0 (no behavioral response). Users must explicitly set values to enable behavioral responses.

## Usage Example

To set CBO-style elasticities for older workers:

```yaml
substitution:
  by_age_position_and_decile:
    65_and_over:
      primary:
        1: 0.50  # Highest elasticity for low-income elderly
        10: 0.30 # Lower for high-income elderly
      secondary: 0.40

income:
  by_age:
    65_and_over: -0.08  # Stronger income effect for elderly
```

## References

- [CBO Working Paper 2012-12: A Review of Recent Research on Labor Supply Elasticities](https://www.cbo.gov/publication/43675)
- [CBO Working Paper 2012-13: Review of Estimates of the Frisch Elasticity of Labor Supply](https://www.cbo.gov/publication/43676)
- French (2005): Elasticities between 0.2 and 0.4 for 40-year-old male heads
- Recent empirical estimates show retirement-age elasticity around 0.8 for extensive margin

## Implementation Notes

- Age is determined from the `age` variable for the year
- Age 65 is the cutoff: age < 65 uses under_65 parameters, age >= 65 uses 65_and_over parameters
- Primary earner is defined as the highest earner within the tax unit
- Earnings deciles are determined using hardcoded markers (TODO: parametrize)
- Negative total earnings result in zero elasticity (using `max_(earnings, 0)`)
