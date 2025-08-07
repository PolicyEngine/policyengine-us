# Affordable Care Act (ACA) Modeling in PolicyEngine

## Overview

This document describes how PolicyEngine simulates the Affordable Care Act (ACA) Marketplace and its premium tax credits.  
It focuses on the mechanics of **premium determination**, **subsidy calculation**, and **state‐specific rules**.

## Key Definitions

- **Second Lowest Cost Silver Plan (SLCSP)** – The silver‐tier plan with the second‐lowest premium in a rating area. It is the benchmark for premium tax credit (PTC) calculations.  
- **Rating areas** – Geographic regions (usually groups of counties) in which insurers must charge the same premium for a given plan and age.  
- **Premium tax credit (PTC)** – A refundable, advanceable credit that caps a household's net premium at a statutory percentage of income. PolicyEngine models the full statutory formula.  
- **Age curves** – Multipliers published by the Centers for Medicare & Medicaid Services (CMS) that scale premiums by age, subject to a federal 3:1 limit (64‑year‑olds pay ≤ 3 × a 21‑year‑old).  
- **Family tier system** – Used only in **New York** and **Vermont**. Premiums vary by family composition (individual, couple, parent‑and‑child, family) rather than age.  
- **Base premium** – The unsubsidized price of the SLCSP normalized to an age‑0 enrollee (chosen for consistency across state age curves).  
- **Marketplace / Exchange** – The online portal (state‑based or HealthCare.gov) where households enroll and apply for subsidies.  
- **Medicaid expansion** – States may extend Medicaid to adults with income ≤ 138 % of the Federal Poverty Line (FPL). Non‑expansion states create a "coverage gap."  
- **Federal Poverty Line (FPL)** – Annual income threshold that scales with household size and is updated each January; PTC formulas reference FPL percentages.

## Background

Under the ACA, insurers may vary premiums **only** by **age**, **rating area (ZIP code)**, and **tobacco use**.  
The PTC formula ignores tobacco loading, so PolicyEngine models price variation on age and location alone.

For each eligible household, the statutory contribution percentage (a sliding scale indexed to the FPL) sets the **maximum share of income** they are expected to spend.  
PolicyEngine calculates the PTC as:

```
PTC = max(0, SLCSP_premium - expected_contribution)
```

where:

```
expected_contribution = contribution_rate(income_pct_FPL) × household_income
```

## Regional Variation in Premiums

1. **Mapping counties to rating areas** – PolicyEngine stores a county → rating‑area crosswalk derived from CMS filings.  
2. **Selecting representative ZIP codes** – One ZIP is chosen per rating area (the modal ZIP or first alphabetically) to query premiums.  
3. **Collecting base premiums** – We batch‑queried the [KFF ACA Premium Calculator](https://www.kff.org/interactive/subsidy-calculator/) for the **2025** plan year, retrieving the SLCSP for a 0‑year‑old in each rating area.  
4. **Normalizing** – All prices are divided by the CMS age‑curve factor for age 0 (1.0) so that age adjustments can be applied uniformly in model logic.

## State‑Specific Quirks

| State / DC | Variation | PolicyEngine Handling |
|------------|-----------|----------------------|
| Six states + DC (**AL, DC, MA, MN, MS, OR, UT**) | Publish their own age curves (not 3:1 capped at age 64) | Store state‑specific vectors; premiums = base × state_age_factor(age) |
| **New York**, **Vermont** | Use a **family tier** (community‑rated) system | Ignore age; premiums selected by tier (`individual`, `couple`, `parent + child`, `family`, `child‑only` in NY) |
| **California** | Has rating area differ by **zip code** | Los Angeles County has 2 rating areas organized by zip code |

## Subsidy Calculation

1. **Determine household MAGI** (modified adjusted gross income) and compute **% FPL** using current‑year poverty guidelines.  
2. **Find SLCSP premium** for each household member:  
   - **Age‑rated**: `premium_age = base × age_curve[state][age]`  
   - **Family‑tiered (NY/VT)**: use tier price, ignoring age.  
3. **Sum monthly premiums** for all covered individuals to get household SLCSP.  
4. **Compute expected contribution** via the statutory schedule (ARPA/IRA enhanced through 2025).  
5. **PTC = max(0, SLCSP – expected contribution)**, capped so net premium ≥ $0.  
6. **Advance payments** are assumed equal to final credit (no reconciliation modeling at this stage).

## Inflation Reduction Act Enhancements (through 2025)

- **Subsidy cliff removal** – Households **> 400 % FPL** remain eligible; the contribution rate plateaus at 8.5 % of income.  
- **Lowered contribution percentages** at every FPL band, reducing net premiums for most enrollees.  

PolicyEngine parameterizes contribution percentages by calendar year, allowing easy extension or sunset of IRA provisions.

## Medicaid Expansion Interaction

For states that **expanded Medicaid**, adults with income ≤ 138 % FPL are diverted to Medicaid and **excluded** from Marketplace simulation.  
In non‑expansion states, PolicyEngine applies the IRA coverage‑gap fix above; individuals below 100 % FPL may still qualify for zero‑premium silver plans via PTC.

## Data Sources

| Data element | Source | Vintage | Parameter Location |
|--------------|--------|---------|--------------------|
| **Federal age curve** | 45 CFR § 156.80(d); CMS *Market Rating Reforms – State-Specific Age Curve Variations* | 2018 + | `gov/aca/age_curves/default.yaml` |
| **State-specific age curves** | CMS *Market Rating Reforms – State-Specific Age Curve Variations* | 2018 + | `gov/aca/age_curves/{state}.yaml`<br/>(AL, DC, MA, MN, MS, NY, OR, UT, VT) |
| **SLCSP premiums by rating area** | Derived from batch scraping (e.g., KFF calculator) | PY 2025 | `gov/aca/state_rating_area_cost.yaml` |
| **Family tier factors (NY/VT)** | CMS *Market Rating Reforms – State-Specific Age Curve Variations* | 2018 + | `gov/aca/family_tier_ratings/{state}.yaml` |
| **Contribution % schedule (PTC phase-out)** | 26 U.S.C. § 36B(b)(3)(A) as amended by ARPA § 9661 & IRA § 12001 | 2015 – 2025 (with ARPA/IRA enhancements) | `gov/aca/ptc_phase_out_rate.yaml` |
| **PTC income-eligibility thresholds** | ACA statutory requirements | By year | `gov/aca/ptc_income_eligibility.yaml` |
| **FPL guidelines** | HHS Poverty Guidelines | Annual updates | `gov/hhs/poverty_guidelines.yaml` |

