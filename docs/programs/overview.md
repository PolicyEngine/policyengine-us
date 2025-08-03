# PolicyEngine US Program Documentation

## Overview

PolicyEngine US is a comprehensive microsimulation model of the United States tax and benefit system. This documentation provides a detailed reference for all programs modeled, including their scope, eligibility criteria, benefit calculations, and legislative sources.

### Scope

The model encompasses:
- **Federal programs**: All major tax credits, deductions, and benefit programs
- **State programs**: Income taxes and benefit programs for all 50 states plus DC
- **Local programs**: Select county and city-level programs
- **Time coverage**: 2017-2030+ with historical values and current law projections

### Organization

Programs are organized by the administering agency:
- [Internal Revenue Service (IRS)](irs/index.md) - Federal taxes and credits
- [Social Security Administration (SSA)](ssa/index.md) - Social Security and SSI
- [Department of Agriculture (USDA)](usda/index.md) - SNAP, WIC, school meals
- [Department of Health and Human Services (HHS)](hhs/index.md) - Medicaid, CHIP, TANF
- [Department of Housing and Urban Development (HUD)](hud/index.md) - Housing assistance
- [Other Federal Programs](other_federal/index.md) - FCC, DOE, ED programs
- [State Programs](states/index.md) - State taxes and benefits
- [Local Programs](local/index.md) - County and city programs

### Key Features

1. **Comprehensive Coverage**: Models virtually all major federal transfer programs and tax provisions
2. **Geographic Variation**: State and local program variations across all jurisdictions
3. **Time Consistency**: Historical accuracy with forward projections under current law
4. **Legislative Grounding**: All parameters traced to authoritative sources
5. **Integration**: Cross-program interactions and eligibility dependencies

### Using This Documentation

Each program section includes:
- **Program Description**: Overview and purpose
- **Eligibility Rules**: Categorical and financial requirements
- **Benefit Calculation**: Formula and parameter values
- **Time Periods**: Years covered and phase-in/out schedules
- **Legislative Sources**: Statutes, regulations, and guidance
- **Key Variables**: PolicyEngine variable names for calculations

### Data Sources

The model uses:
- **Current Population Survey (CPS)**: Primary microdata source
- **American Community Survey (ACS)**: Geographic supplementation
- **Administrative Data**: Calibration targets from agency reports
- **Legislative Texts**: Parameter values from statutes and regulations