"""
Connecticut TFA extension period benefit reduction for high earners.
"""

from policyengine_us.model_api import *


class ct_tfa_extension_benefit_reduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA extension period benefit reduction"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut reduces TFA benefits by 20% for families with earnings "
        "between 171% and 230% of Federal Poverty Level during the extension "
        "period (effective January 1, 2024).\n\n"
        "Extension Period Policy:\n"
        "  - Effective: January 1, 2024\n"
        "  - Purpose: Allow working families to transition off TFA gradually\n"
        "  - Duration: Up to 6 consecutive months after earnings exceed 100% FPL\n"
        "  - Eligibility: Earnings disregarded up to 230% FPL\n"
        "  - Benefit reduction: 20% reduction if earnings between 171% and 230% FPL\n\n"
        "Income Thresholds (2024 FPL):\n"
        "  Below 100% FPL: Full benefit, no reduction\n"
        "  100%-171% FPL: Full benefit (countable income may reduce benefit)\n"
        "  171%-230% FPL: 20% benefit reduction applies\n"
        "  Above 230% FPL: Ineligible for TFA\n\n"
        "Example 1 - No reduction (Family of 3, $3,000/month earnings):\n"
        "  - Gross earned income: $3,000/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Percent of FPL: $3,000 / $2,152 = 139%\n"
        "  - Lower threshold (171% FPL): $2,152 × 1.71 = $3,680\n"
        "  - Earnings below 171% FPL: No extension reduction\n"
        "  - Extension reduction: $0\n\n"
        "Example 2 - Reduction applies (Family of 3, $4,000/month earnings):\n"
        "  - Gross earned income: $4,000/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Percent of FPL: $4,000 / $2,152 = 186%\n"
        "  - Lower threshold (171% FPL): $3,680\n"
        "  - Upper threshold (230% FPL): $4,950\n"
        "  - Earnings in reduction range: Yes (171%-230%)\n"
        "  - Base benefit: $698 (payment standard) - $0 (income disregarded)\n"
        "  - Extension reduction (20%): $698 × 0.20 = $139.60\n"
        "  - Final benefit: $698 - $139.60 = $558.40/month\n\n"
        "Example 3 - At upper threshold (Family of 3, $4,900/month earnings):\n"
        "  - Gross earned income: $4,900/month\n"
        "  - FPL for 3 (2024): $2,152/month\n"
        "  - Percent of FPL: $4,900 / $2,152 = 228%\n"
        "  - Upper threshold (230% FPL): $4,950\n"
        "  - Earnings just under 230%: Reduction applies\n"
        "  - Base benefit: $698\n"
        "  - Extension reduction (20%): $698 × 0.20 = $139.60\n"
        "  - Final benefit: $558.40/month\n\n"
        "Example 4 - Above threshold (Family of 3, $5,000/month earnings):\n"
        "  - Gross earned income: $5,000/month\n"
        "  - Percent of FPL: $5,000 / $2,152 = 232%\n"
        "  - Above 230% FPL: Ineligible (caught by income eligibility test)\n"
        "  - Extension reduction: $0 (household ineligible)\n\n"
        "Related Variables:\n"
        "  - ct_tfa_income_eligible: Tests earnings against 230% FPL threshold\n"
        "  - ct_tfa_gross_earned_income: Used to determine FPL percentage\n"
        "  - ct_tfa_countable_income: Earnings disregarded up to 100% FPL\n"
        "  - ct_tfa: Final benefit applies this reduction\n\n"
        "Policy Note:\n"
        "This extension period policy helps families transition from TFA to "
        "self-sufficiency by allowing them to continue receiving reduced benefits "
        "while their earnings increase, rather than losing all benefits suddenly "
        "when income crosses a threshold."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Extension Period Section; "
        "Public Act 22-118 (2022) - TFA Program Modernization; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        # Consolidate parameter access for better performance
        p = parameters(
            period
        ).gov.states.ct.dss.tfa.extension_benefit_reduction
        fpg = parameters(period).gov.hhs.fpg

        # Get gross earned income to test against FPL thresholds
        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)

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

        # Determine if earnings fall in the 20% reduction range
        # Reduction applies when earnings are between 171% and 230% of FPL
        # Connecticut TANF State Plan 2024-2026, effective January 1, 2024

        # Lower threshold: 171% of FPL
        # reduction_threshold_lower = 1.71
        # Example: $2,152 × 1.71 = $3,680
        lower_threshold = monthly_fpl * p.reduction_threshold_lower

        # Upper threshold: 230% of FPL
        # reduction_threshold_upper = 2.3
        # Example: $2,152 × 2.30 = $4,950
        upper_threshold = monthly_fpl * p.reduction_threshold_upper

        # Check if gross earnings fall in the reduction range
        # Example: $4,000 >= $3,680 AND $4,000 <= $4,950 → True
        in_reduction_range = (gross_earned >= lower_threshold) & (
            gross_earned <= upper_threshold
        )

        # Calculate base benefit (before extension reduction)
        # This is payment standard minus countable income
        # During extension period, earnings are disregarded up to 100% FPL
        # for countable income calculation, so countable income may be low/zero
        payment_standard = spm_unit("ct_tfa_payment_standard", period)
        countable_income = spm_unit("ct_tfa_countable_income", period)
        base_benefit = max_(payment_standard - countable_income, 0)

        # Apply 20% reduction if earnings are in the 171%-230% FPL range
        # reduction_rate = 0.2 (20%)
        # Example: $698 × 0.20 = $139.60
        reduction = where(
            in_reduction_range, base_benefit * p.reduction_rate, 0
        )

        # Return the reduction amount
        # This will be subtracted from base benefit in ct_tfa.py
        return reduction
