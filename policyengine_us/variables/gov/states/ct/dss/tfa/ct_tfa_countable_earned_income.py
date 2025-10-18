"""
Connecticut TFA countable earned income after disregards.
"""

from policyengine_us.model_api import *


class ct_tfa_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA countable earned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut TFA earned income after applying the continuing eligibility "
        "100% earned income disregard.\n\n"
        "Disregard Rules (by enrollment status):\n"
        "  At Initial Application:\n"
        "    - $90 deducted from each earner's gross earnings\n"
        "    - Must have gross earned income < 55% FPL to qualify\n\n"
        "  Continuing Eligibility (enrolled households):\n"
        "    - 100% of earnings disregarded up to 100% FPL\n"
        "    - Earnings above 100% FPL are countable\n\n"
        "  Extension Period (effective January 1, 2024):\n"
        "    - 100% of earnings disregarded up to 230% FPL for eligibility\n"
        "    - Earnings between 171% and 230% FPL trigger 20% benefit reduction\n"
        "    - Earnings above 230% FPL = ineligible\n\n"
        "Example 1 - Low earner (Family of 3, $800/month earnings):\n"
        "  - Gross earned income: $800/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Percent of FPL: $800 / $2,152 = 37%\n"
        "  - Continuing disregard limit (100% FPL): $2,152\n"
        "  - Disregard: min($800, $2,152) = $800\n"
        "  - Countable earned income: $800 - $800 = $0\n\n"
        "Example 2 - Moderate earner (Family of 3, $2,500/month earnings):\n"
        "  - Gross earned income: $2,500/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Percent of FPL: $2,500 / $2,152 = 116%\n"
        "  - Continuing disregard limit (100% FPL): $2,152\n"
        "  - Disregard: min($2,500, $2,152) = $2,152\n"
        "  - Countable earned income: $2,500 - $2,152 = $348\n\n"
        "Example 3 - High earner in extension period (Family of 3, $4,000/month):\n"
        "  - Gross earned income: $4,000/month\n"
        "  - FPL for 3: $2,152/month\n"
        "  - Percent of FPL: $4,000 / $2,152 = 186%\n"
        "  - Still eligible (under 230% FPL threshold)\n"
        "  - Continuing disregard limit (100% FPL): $2,152\n"
        "  - Disregard: min($4,000, $2,152) = $2,152\n"
        "  - Countable earned income: $4,000 - $2,152 = $1,848\n"
        "  - Note: Extension reduction will apply separately\n\n"
        "Related Variables:\n"
        "  - ct_tfa_gross_earned_income: Starting point before disregards\n"
        "  - ct_tfa_income_eligible: Tests earnings against FPL thresholds\n"
        "  - ct_tfa_extension_benefit_reduction: 20% reduction for 171%-230% FPL\n"
        "  - ct_tfa_countable_income: Combines this with countable unearned income\n\n"
        "Note: Student income is fully disregarded per Conn. Gen. Stat. § 17b-80."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Disregard Section; "
        "Conn. Gen. Stat. § 17b-80 (Student Income Disregard); "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf; "
        "https://www.lawserver.com/law/state/connecticut/ct-laws/connecticut_statutes_17b-80"
    )

    def formula(spm_unit, period, parameters):
        # Consolidate parameter access for better performance
        p = parameters(period).gov.states.ct.dss.tfa
        fpg = parameters(period).gov.hhs.fpg

        # Get gross earned income (before any disregards)
        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)

        # Get assistance unit size for FPL calculation
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Calculate Federal Poverty Level for household size
        # Example: For family of 3 in 2024:
        #   Base (1 person): $15,060/year
        #   Additional persons (2): 2 × $5,380 = $10,760
        #   Annual FPL: $15,060 + $10,760 = $25,820
        #   Monthly FPL: $25,820 / 12 = $2,152
        annual_fpl = fpg.first_person + fpg.additional_person * max_(
            size - 1, 0
        )
        monthly_fpl = annual_fpl / 12

        # Apply continuing eligibility disregard: 100% of earnings up to 100% FPL
        # This implements Connecticut's generous earned income disregard policy
        # which allows working families to keep more of their TFA benefits
        # Connecticut TANF State Plan 2024-2026, Income Disregard Section

        # Calculate the disregard limit (100% of FPL)
        # income_limits.continuing = 1.0 (100% FPL)
        continuing_limit = monthly_fpl * p.income_limits.continuing

        # Disregard is the lesser of actual earnings or the 100% FPL limit
        # Example: If earnings = $800 and FPL = $2,152, disregard = $800
        # Example: If earnings = $2,500 and FPL = $2,152, disregard = $2,152
        disregard = min_(gross_earned, continuing_limit)

        # Countable earned income = gross earnings minus disregard
        # Cannot be negative (use max_ to ensure zero floor)
        # Example: $2,500 - $2,152 = $348 countable
        return max_(gross_earned - disregard, 0)
