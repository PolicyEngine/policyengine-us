# Temporary Assistance for Needy Families (TANF)

Currently in development, TANF is a state-level benefit program.

From benefits.gov:

> The Temporary Assistance for Needy Families (TANF) program provides grant funds to states and territories to provide families with financial assistance and related support services. State-administered programs may include childcare assistance, job preparation, and work assistance.

## General formula

To calculate TANF entitlement, we use the general computation tree below (may vary depending on state and county):

- `tanf`: TANF entitlement
  - `tanf_amount_if_eligible`: amount if eligible
    - Definition: `tanf_max_amount - tanf_reduction`
    - `tanf_max_amount`: maximum amount
      - **Paramters**: the maximum amount defined bydifferent state TANF programs may vary due to these factors:
        - Household size: How many people live in the household.
        - "Region": Some states may define a "region"-level distinction for maximum amounts; for example, California (CalWORKS) defines two regions based on what county the household resides in.
        - Individual household properties such as caregiver or disability status.
        - Example: California (CalWORKS) has different maximum amounts based on these factors, which they define as "exempt/non-exempt".
        - State-specific policies.
    - `tanf_reduction` (currently `tanf_countable_income`; CHANGE): Reduction from income
      - `tanf_gross_earned_income`: earned income.
        - **Parameter**: list of earned income sources summed.
      - `tanf_gross_unearned_income`: unearned income. (ADD DEF HERE)
        - **Parameter**: list of unearned income sources summed.
      - `deductions`: deductions from assessed income.
        - `earnings_deduction`: deduction amount based on earnings.
          - **Parameter**: percentage of earnings deducted from gross earned income.
          - **Parameter**: flat amount deducted from the household's gross earned income.
          - **Parameter**: flat amount deducted from each earner's gross earned income.
  - `is_tanf_eligible`: whether eligible for TANF
    - `is_tanf_enrolled`: whether a family is already enrolled in TANF.
    - `is_tanf_demographically_eligible`: demographic definition of TANF eligibility, which is mostly constant across the US.
      - Definition: If there are children (ages 0-17) present in the household, pregnant people, or there are people aged 18 years old that are currently enrolled in a school, the family is demographically eligible for TANF.
    - `is_tanf_economically_eligible`: Whether the family has sufficiently low income to qualify for eligibility.
      - `is_tanf_enrolled`: whether a family is already enrolled in TANF.
      - `is_tanf_continuous_eligible`:
        - `tanf_eligibility_income`: income measure used to assess eligibility for TANF.
          - **Parameters**: income definition varies depending on state policies:
            - **Parameter**: deductions from income per earner
            - **Parameter**: deductions from income per household
        - `tanf_max_amount` (defined above)
      - `is_tanf_initial_eligible`:
        - This variable is very similar to `is_continuous_eligible`, except for the initial employment deductions that are applied to determininig initial eligibility.
        - `tanf_eligibility_income`: income measure used to assess eligibility for TANF.
          - **Parameters**: income definition varies depending on state policies:
            - **Parameter**: deductions from income per earner
            - **Parameter**: deductions from income per household
        - `tanf_max_amount` (defined above)
