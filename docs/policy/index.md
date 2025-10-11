# PolicyEngine US Policy Reference

This reference provides comprehensive documentation of all tax and benefit program rules in PolicyEngine US.

## Organization

This documentation separates policy design and legislative context from technical implementation:

- **Policy Reference** (this section): Program rules, eligibility criteria, benefit formulas, and legislative history
- **[Technical Examples](../examples/index)**: Code examples and implementation details
- **[API Documentation](../api/index)**: Function reference and programmatic access

## Federal Programs

### [Taxation](federal/taxation/index)
- [Income Tax System](federal/taxation/income/index) - Progressive rate structure, deductions, and credits
- [Payroll Taxes](federal/taxation/payroll/index) - Social Security and Medicare financing

### [Transfer Programs](federal/transfers/index)
- [Safety Net Programs](federal/transfers/safety-net/index) - SNAP, TANF, Medicaid
- [Social Insurance](federal/transfers/social-insurance/index) - Social Security, Unemployment Insurance

## [State Programs](state/index)

Comprehensive modeling of all 50 states plus DC, including:
- State income tax systems
- State-specific tax credits (EITC supplements, CTCs)
- State benefit programs (TANF implementations)

## [Program Interactions](interactions/index)

Critical cross-program effects:
- [Benefit Cliffs](interactions/cliff-effects) - Marginal rate discontinuities
- [Cumulative Tax Rates](interactions/marginal-rates) - Combined federal/state/local burdens
- [Reform Interactions](interactions/reform-impacts) - Cross-program policy change effects

## Key Features

### Legislative Grounding
Every parameter is traced to authoritative sources:
- United States Code (USC) citations
- Code of Federal Regulations (CFR) references
- State statutory citations
- IRS Revenue Procedures and Notices

### Time Coverage
- Historical accuracy: 2017-present with actual parameter values
- Current law baseline: Projects forward under existing law
- Reform modeling: Alternative policy scenarios

### Geographic Variation
- Federal rules with state-specific variations
- Local programs in major jurisdictions
- Cost-of-living adjustments where applicable

## Using This Reference

### Navigation
- Browse by federal agency (IRS, SSA, USDA, etc.)
- Search for specific programs or parameters
- View state-specific implementations

## Data Sources

### Parameters
- **Legislative Texts**: Direct statutory values
- **Regulatory Guidance**: Agency interpretations
- **Inflation Adjustments**: BLS indices for uprating

## Citation

When using PolicyEngine US in research:

```
@software{policyengine2024,
  author = {{PolicyEngine}},
  title = {PolicyEngine US: Open-Source Tax and Benefit System},
  url = {https://github.com/PolicyEngine/policyengine-us},
  version = {0.800.0},
  year = {2024}
}
```

For specific program parameters, cite both PolicyEngine and the underlying legislative source.