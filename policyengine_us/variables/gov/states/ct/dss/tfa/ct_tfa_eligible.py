"""
Connecticut TFA overall eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA eligibility"
    definition_period = MONTH
    defined_for = StateCode.CT
    documentation = (
        "Overall eligibility for Connecticut Temporary Family Assistance (TFA) "
        "program, Connecticut's implementation of federal TANF.\n\n"
        "Eligibility Requirements (ALL must be met):\n\n"
        "1. Demographic Requirements:\n"
        "   - Family has dependent children under age 18, OR\n"
        "   - Children age 18 enrolled full-time in school, OR\n"
        "   - Pregnant woman in household\n\n"
        "2. Income Requirements:\n"
        "   - Gross earned income < 230% FPL (extension period maximum)\n"
        "   - Gross unearned income < 55% FPL (standard of need)\n\n"
        "3. Resource Requirements:\n"
        "   - Total countable assets < $6,000\n"
        "   - Vehicle equity < $9,500 (one vehicle excluded)\n"
        "   - Home property not counted\n\n"
        "Example 1 - Eligible household:\n"
        "  Demographic: Single mother with 2 children (ages 5, 8) ✓\n"
        "  Income: Earns $1,500/month, no unearned income ✓\n"
        "  Resources: $2,000 in bank account, owns car worth $5,000 ✓\n"
        "  → TFA eligible: Yes\n\n"
        "Example 2 - Income too high:\n"
        "  Demographic: Two-parent family with 1 child ✓\n"
        "  Income: Combined earnings $6,000/month ✗ (over 230% FPL)\n"
        "  Resources: $1,000 in savings ✓\n"
        "  → TFA eligible: No (income too high)\n\n"
        "Example 3 - Assets too high:\n"
        "  Demographic: Single parent with 1 child ✓\n"
        "  Income: Earns $1,000/month ✓\n"
        "  Resources: $8,000 in bank account ✗ (over $6,000 limit)\n"
        "  → TFA eligible: No (resources exceed limit)\n\n"
        "Example 4 - No qualifying children:\n"
        "  Demographic: Childless couple ✗\n"
        "  Income: Earns $800/month ✓\n"
        "  Resources: $500 in savings ✓\n"
        "  → TFA eligible: No (no dependent children)\n\n"
        "Example 5 - Pregnant woman eligible:\n"
        "  Demographic: Pregnant woman, no current children ✓\n"
        "  Income: Earns $900/month ✓\n"
        "  Resources: $1,500 in savings ✓\n"
        "  → TFA eligible: Yes\n\n"
        "Related Variables:\n"
        "  - ct_tfa_demographic_eligible: Has children or pregnant member\n"
        "  - ct_tfa_income_eligible: Earnings/unearned income tests\n"
        "  - ct_tfa_resources_eligible: Asset limit test\n"
        "  - ct_tfa: Benefit amount (if eligible)\n\n"
        "Note: Additional requirements not currently modeled include:\n"
        "  - Residency in Connecticut\n"
        "  - U.S. citizenship or qualified immigration status\n"
        "  - Social Security Number\n"
        "  - Cooperation with child support enforcement\n"
        "  - Work requirements (for able-bodied adults)"
    )
    reference = (
        "Conn. Gen. Stat. § 17b-112 (TFA Program Authorization); "
        "Connecticut TANF State Plan 2024-2026; "
        "Connecticut TFA Fact Sheet - Eligibility Requirements; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf; "
        "https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        # Test 1: Demographic eligibility
        # Must have dependent children under 18 (or 18 if in school full-time)
        # OR have a pregnant member in the household
        # Connecticut TANF State Plan 2024-2026, Eligibility Criteria
        demographic_eligible = spm_unit(
            "ct_tfa_demographic_eligible", period.this_year
        )

        # Test 2: Income eligibility
        # Earned income must be < 230% FPL (extension period maximum)
        # Unearned income must be < 55% FPL (standard of need)
        # Connecticut TANF State Plan 2024-2026, Income Eligibility Section
        income_eligible = spm_unit("ct_tfa_income_eligible", period)

        # Test 3: Resource eligibility
        # Total countable assets must be < $6,000
        # One vehicle excluded if equity < $9,500
        # Home property not counted
        # Connecticut TANF State Plan 2024-2026, Asset Limits
        resources_eligible = spm_unit(
            "ct_tfa_resources_eligible", period.this_year
        )

        # Household is TFA eligible only if ALL three tests pass
        # If any test fails, household is ineligible
        return demographic_eligible & income_eligible & resources_eligible
