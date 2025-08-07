# Temporary Assistance for Needy Families (TANF)

## Overview

Temporary Assistance for Needy Families provides time-limited cash assistance to low-income families with children. PolicyEngine US models TANF cash assistance benefits for states where detailed rules are implemented, recognizing the significant state variation in this block grant program.

## Program Structure

### Block Grant Design

TANF operates as a federal block grant where:
- States have broad flexibility in design
- Federal requirements set minimum standards
- Time limits and work requirements apply
- Multiple uses beyond cash assistance

### State Implementation

PolicyEngine US currently models state-specific TANF programs for:
- **California** (CalWORKs)
- **Colorado**
- **District of Columbia**
- **Illinois**
- **New York**
- **North Carolina**
- **Oklahoma**

Note: The main TANF variable currently aggregates benefits from CA, CO, DC, and NY. Other state implementations may require direct access to state-specific variables.

## Modeled Variables

### Input Variables
- `age`: For dependent child eligibility
- `is_pregnant`: Some states cover pregnant women
- Employment and unearned income
- Family relationships and composition
- Resources/assets (varies by state)

### Calculated Variables
- `tanf`: Total TANF cash benefit
- `tanf_reported`: Self-reported TANF receipt
- State-specific variables (e.g., `ca_tanf`, `co_tanf`)

### State-Specific Components
Each modeled state includes:
- Income eligibility limits
- Benefit calculation formulas
- Income disregards
- Resource limits
- Special provisions

### Not Currently Modeled
- Non-cash TANF services
- Child care assistance through TANF
- Work participation tracking
- Time limit counters
- Sanctions and compliance
- Many state programs

## Legislative References

**Primary Authority**: Personal Responsibility and Work Opportunity Reconciliation Act of 1996

**Federal Requirements**: 42 USC Chapter 7, Subchapter IV, Part A

**State Authority**: Individual state TANF plans

## Program Requirements

Federal TANF includes:
- **60-month lifetime limit**: Federal funds
- **Work requirements**: After 24 months
- **Family cap**: State option
- **Teen parent provisions**: School/living requirements

## State Variations

States determine:
- Benefit levels and calculation methods
- Income and resource limits
- Exemptions and extensions
- Sanction policies
- Additional state-funded benefits

## Income Treatment

Common elements across states:
- Earned income disregards
- Treatment of child support
- Unearned income counting
- Lump sum rules
- Income averaging periods

## Program Interactions

TANF interacts with:
- **SNAP**: Categorical eligibility
- **Medicaid**: Transitional coverage
- **Child Care**: Priority access
- **Child Support**: Cooperation requirements
- **SSI**: Generally exclusive

## Special Populations

TANF serves:
- Single-parent families
- Two-parent families (state option)
- Minor parents
- Relative caregivers
- Families with disabilities

## Data Considerations

The model uses:
- State TANF plan parameters
- Administrative data where available
- Benefit calculators for validation
- Take-up rates vary significantly by state