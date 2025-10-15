"""
Connecticut Temporary Family Assistance (TFA) benefit amount.
"""

from policyengine_us.model_api import *


class ct_tfa(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA benefit"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Monthly cash assistance benefit amount from Connecticut's Temporary Family "
        "Assistance (TFA) program, Connecticut's implementation of federal TANF.\n\n"
        "Calculation Process:\n"
        "1. Start with payment standard for household's region and size\n"
        "2. Subtract countable income (after disregards)\n"
        "3. Subtract family cap reduction (if applicable)\n"
        "4. Subtract extension period reduction (if applicable)\n"
        "5. Result cannot be less than zero\n\n"
        "Example 1 - Basic case (Family of 3, Region A, no income):\n"
        "  - Payment standard: $698/month\n"
        "  - Countable income: $0\n"
        "  - Family cap reduction: $0\n"
        "  - Extension reduction: $0\n"
        "  - TFA benefit: $698/month\n\n"
        "Example 2 - With earned income (Family of 3, Region A, $800/month earnings):\n"
        "  - Payment standard: $698/month\n"
        "  - Gross earned income: $800/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Income fully disregarded (under 100% FPL)\n"
        "  - Countable income: $0\n"
        "  - TFA benefit: $698/month\n\n"
        "Example 3 - Extension period with high earnings (Family of 3, $4,000/month):\n"
        "  - Payment standard: $698/month\n"
        "  - Gross earned income: $4,000/month (186% FPL)\n"
        "  - Income disregarded for eligibility (between 100% and 230% FPL)\n"
        "  - Countable income: $0\n"
        "  - Base benefit: $698\n"
        "  - Extension reduction (20% for 171%-230% FPL): $698 × 0.20 = $139.60\n"
        "  - TFA benefit: $698 - $139.60 = $558.40/month\n\n"
        "Example 4 - Family cap (New child born 8 months after application):\n"
        "  - Payment standard increased from $563 (size 2) to $698 (size 3)\n"
        "  - Increment: $698 - $563 = $135\n"
        "  - Family cap reduction (50%): $135 × 0.50 = $67.50\n"
        "  - Effective increment: $135 - $67.50 = $67.50\n"
        "  - If no other income: $563 + $67.50 = $630.50/month\n\n"
        "Related Variables:\n"
        "  - ct_tfa_eligible: Overall eligibility determination\n"
        "  - ct_tfa_payment_standard: Base benefit amount\n"
        "  - ct_tfa_countable_income: Income after all disregards\n"
        "  - ct_tfa_family_cap_reduction: Reduction for recent births\n"
        "  - ct_tfa_extension_benefit_reduction: Reduction for high earners\n\n"
        "Note: Public Act 22-118 (July 1, 2022) made TFA benefits uniform statewide "
        "and indexed to 55% of Federal Poverty Level. Historical regional variations "
        "(2014-2022) are maintained in parameters for historical analysis only."
    )
    reference = (
        "Conn. Gen. Stat. § 17b-112 (TFA Program Authorization); "
        "Connecticut TANF State Plan 2024-2026; "
        "Public Act 22-118 (2022) - Statewide Uniform Benefits; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        # Check overall eligibility (demographic, income, and resource tests)
        eligible = spm_unit("ct_tfa_eligible", period)

        # Step 1: Get payment standard based on region and household size
        # This is the maximum benefit the household could receive with zero income
        # Example: Family of 3 in Region A = $698/month
        payment_standard = spm_unit("ct_tfa_payment_standard", period)

        # Step 2: Calculate countable income after all disregards
        # Includes both earned and unearned income after applying:
        # - 100% earned income disregard up to 100% FPL
        # - $50 child support passthrough
        # - Full SSI exclusion
        countable_income = spm_unit("ct_tfa_countable_income", period)

        # Step 3: Calculate base benefit (payment standard minus countable income)
        # This is the benefit before any family cap or extension reductions
        # Example: $698 - $0 = $698
        base_benefit = max_(payment_standard - countable_income, 0)

        # Step 4: Apply family cap reduction if applicable
        # Reduces benefit increase by 50% for children born within 10 months
        # of initial TFA application (Connecticut's partial family cap)
        # Conn. Gen. Stat. § 17b-688b
        family_cap_reduction = spm_unit("ct_tfa_family_cap_reduction", period)

        # Step 5: Apply extension period benefit reduction if applicable
        # For earnings between 171% and 230% FPL during extension period:
        # benefit reduced by 20% (effective January 1, 2024)
        # CT TANF State Plan 2024-2026
        extension_reduction = spm_unit(
            "ct_tfa_extension_benefit_reduction", period
        )

        # Step 6: Calculate final benefit
        # Subtract all reductions, ensuring benefit doesn't go negative
        final_benefit = max_(
            base_benefit - family_cap_reduction - extension_reduction, 0
        )

        # Return benefit only if household is eligible, otherwise $0
        return where(eligible, final_benefit, 0)
