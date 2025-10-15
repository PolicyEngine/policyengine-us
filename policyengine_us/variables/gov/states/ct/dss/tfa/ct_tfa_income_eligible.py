"""
Connecticut TFA income eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA income eligibility"
    definition_period = MONTH
    defined_for = StateCode.CT
    documentation = (
        "Connecticut TFA income eligibility determination using graduated thresholds.\n\n"
        "Income Eligibility Rules:\n"
        "  - Earned income must be under 230% FPL (extension period maximum)\n"
        "  - Unearned income must be under 55% FPL (standard of need)\n\n"
        "Tiered System:\n"
        "  1. Initial/Standard of Need (55% FPL): New applicants\n"
        "  2. Continuing Eligibility (100% FPL): Enrolled households\n"
        "  3. Extension Period (230% FPL): Up to 6 months after exceeding 100% FPL\n\n"
        "Example 1 - New applicant, eligible (Family of 3):\n"
        "  - Gross earned income: $1,000/month\n"
        "  - Gross unearned income: $0\n"
        "  - FPL: $2,152/month\n"
        "  - Earned income (46% FPL): Under 230% threshold ✓\n"
        "  - Unearned income (0% FPL): Under 55% threshold ✓\n"
        "  - Income eligible: Yes\n\n"
        "Example 2 - Continuing household, eligible (Family of 3):\n"
        "  - Gross earned income: $2,000/month\n"
        "  - Gross unearned income: $100/month\n"
        "  - FPL: $2,152/month\n"
        "  - Earned income (93% FPL): Under 230% threshold ✓\n"
        "  - Unearned income (5% FPL): Under 55% threshold ✓\n"
        "  - Income eligible: Yes\n\n"
        "Example 3 - Extension period, eligible (Family of 3):\n"
        "  - Gross earned income: $4,500/month\n"
        "  - Gross unearned income: $50/month\n"
        "  - FPL: $2,152/month\n"
        "  - Earned income (209% FPL): Under 230% threshold ✓\n"
        "  - Unearned income (2% FPL): Under 55% threshold ✓\n"
        "  - Income eligible: Yes (extension period)\n\n"
        "Example 4 - Too high earnings, ineligible (Family of 3):\n"
        "  - Gross earned income: $5,000/month\n"
        "  - Gross unearned income: $0\n"
        "  - FPL: $2,152/month\n"
        "  - Earned income (232% FPL): Over 230% threshold ✗\n"
        "  - Income eligible: No\n\n"
        "Example 5 - Too high unearned, ineligible (Family of 3):\n"
        "  - Gross earned income: $500/month\n"
        "  - Gross unearned income: $1,500/month\n"
        "  - FPL: $2,152/month\n"
        "  - Unearned income (70% FPL): Over 55% threshold ✗\n"
        "  - Income eligible: No\n\n"
        "Related Variables:\n"
        "  - ct_tfa_gross_earned_income: Tested against 230% FPL\n"
        "  - ct_tfa_gross_unearned_income: Tested against 55% FPL\n"
        "  - ct_tfa_eligible: Combines this with demographic and resource tests\n"
        "  - ct_tfa_countable_earned_income: Applies disregards after eligibility\n\n"
        "Implementation Note:\n"
        "This simplified implementation uses the extension limit (230% FPL) as the\n"
        "maximum earned income threshold, covering all three tiers. Actual enrollment\n"
        "status tracking would require additional state variables."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Eligibility Section; "
        "Conn. Gen. Stat. § 17b-112 (TFA Program Authorization); "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm"
    )

    def formula(spm_unit, period, parameters):
        # Consolidate parameter access for better performance
        p = parameters(period).gov.states.ct.dss.tfa
        fpg = parameters(period).gov.hhs.fpg

        # Get gross income amounts (before any disregards)
        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)
        gross_unearned = spm_unit("ct_tfa_gross_unearned_income", period)

        # Get household size for FPL calculation
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

        # Test earned income against extension period maximum (230% FPL)
        # This is the highest threshold, covering all enrollment statuses:
        # - Initial applicants: 55% FPL
        # - Continuing households: 100% FPL
        # - Extension period: 230% FPL
        # income_limits.extension = 2.3 (230%)
        # Example: $2,152 × 2.3 = $4,950
        extension_limit = monthly_fpl * p.income_limits.extension

        # Test unearned income against standard of need (55% FPL)
        # This is Connecticut's initial eligibility threshold
        # income_limits.initial = 0.55 (55%)
        # Example: $2,152 × 0.55 = $1,184
        initial_limit = monthly_fpl * p.income_limits.initial

        # Income eligible if BOTH conditions met:
        # 1. Gross earned income < 230% FPL (extension maximum)
        # 2. Gross unearned income < 55% FPL (standard of need)
        # Example: $4,000 < $4,950 AND $100 < $1,184 → True
        return (gross_earned < extension_limit) & (
            gross_unearned < initial_limit
        )
