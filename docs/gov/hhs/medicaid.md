# Medicaid 

## 1  Overview

PolicyEngine simulates Medicaid eligibility, enrollment, and spending for every individual in its micro‑simulation population. The model applies statutory and regulatory rules to  household‑level data, assigns each enrollee to a mutually‑exclusive **MACPAC** category, and assigns a per‑capita costs. 

## 2  Key Data Inputs

| Source | Vintage | Key variables |
|--------|---------|---------------|
| Enhanced CPS ASEC | 2024 micro‑data | `age`, `state`, household income, disability status, SSI receipt |
| MACPAC Exhibit 21 | Published Dec 2024 (data year 2022) | Enrollment & per‑capita spending by eligibility group |
| MACPAC projections | April 2024 release | National Medicaid spending & enrollment totals |

Additional parameters (e.g. **Federal Poverty Guidelines**, FMAP) come from CMS and FNS administrative releases bundled with PolicyEngine.

## 3  Eligibility Determination

For each person $p$ in period $t$ (calendar year):

1. **Financial test** – compare household *modified income* to the relevant FPL threshold for the individual's state, age, pregnancy, and parent/caretaker status.
2. **Categorical tests**:
   - **SSI‑linked** — aged 65+, blind, or meeting SSA disability criteria.
   - **Blindness & disability** — uses CPS ASEC disability flags and SSI receipt as a proxy where SRDI data are unavailable.
   - **Expansion adult** — aged 19–64 *and* in a Medicaid‑expansion state, income ≤ 138 % FPL, not otherwise mandatory.
3. **Residency & immigration filters** — five‑year bar, lawfully‑present exemptions, refugees, etc.

The implementation lives in `is_medicaid_eligible` (`policyengine_us/variables/gov/hhs/medicaid/eligibility.py`), which aggregates the sub‑tests and returns a Boolean array.

## 4  Mapping to MACPAC Eligibility Groups

| MACPAC group | PolicyEngine mapping logic |
|--------------|----------------------------|
| **Child** | `age < 19` |
| **New adult group** | `is_medicaid_eligible & expansion_state & 19 ≤ age ≤ 64 & not parent/caretaker` |
| **Other adult** | Parent/caretaker adults (pre‑ACA mandatory & optional parents) |
| **Disabled** | `is_disabled OR receives_ssi` (under 65) |
| **Aged** | `age ≥ 65` and not captured above |

Each person's categorical assignment is produced by the `medicaid_group` variable (a fast NumPy `Enum`).

## 5  Per‑Capita Cost Parameters

MACPAC's July 2024 release supplies the most recent nationally‑consistent spending per enrollee (FY 2022, **inflated to 2024 dollars** using the CMS price index):

| Group | Per‑capita cost (USD, CY 2024) |
|-------|-------------------------------:|
| Child | $3,540 |
| New adult | $7,055 |
| Other adult | $5,007 |
| Disabled | $21,298 |
| Aged | $21,298 |

_MACPAC reports **Aged** and **Disabled** separately; PolicyEngine combines them for simplicity._

The YAML parameter files live under
`policyengine_us/parameters/calibration/gov/hhs/medicaid/totals/per_capita/`.

## 6  Simulating Take‑Up and Enrollment

Eligibility does **not** guarantee participation. For each eligibility group, PolicyEngine:

1. Draws a reproducible pseudo‑random seed `medicaid_take_up_seed`.
2. Compares the seed to an externally‑sourced take‑up probability (e.g. 93 % for children, 82 % for disabled adults).

This yields a binary flag `is_medicaid_enrolled`, which—together with `medicaid_group`—feeds spending calculations.

## 7  Calibration to 2024 National Totals

State‑level CMS‑64 data lag by roughly two years, so PolicyEngine calibrates to **national** 2024 aggregates.
- **Target**: CMS National Health Expenditure (NHE) projects **$826 billion** in total Medicaid spending for CY 2024.
- **Target**: MACPAC reports **72,429,055** full‑benefit enrollees in CY 2024.

## 8  Known Limitations & Roadmap

- **Long‑term services & supports (LTSS)** – currently embedded in per‑capita costs rather than modeled separately.
- **Non‑citizen eligibility complexity** – point‑in‑time CPS immigration variables only approximate five‑year‑bar exceptions.
- **Dynamic macro feedback** – behavioral changes (e.g. employer insurance offer) are not yet endogenously simulated.

Planned improvements:
1. Incorporate CMS‑64 state files on a rolling basis.
2. Add person‑level LTSS flags from NHIS.

## 9  References

1. MACPAC. **MACStats: Medicaid and CHIP Data Book**, Exhibits 14 & 36. July 2024.
2. Centers for Medicare & Medicaid Services. **National Health Expenditure Projections 2024 – 2033**. April 2024.
3. U.S. Census Bureau. **Current Population Survey, Annual Social and Economic Supplement (ASEC) 2024**.

