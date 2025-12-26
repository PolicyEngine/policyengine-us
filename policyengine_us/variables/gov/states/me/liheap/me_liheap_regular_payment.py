from policyengine_us.model_api import *


class me_liheap_regular_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine LIHEAP regular heating assistance payment"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "docs/agents/sources/me-liheap/benefit_calculation.md",
        "docs/agents/sources/me-liheap/maine_liheap_overview.md",
        "42 U.S.C. § 8624(b)(2) - Benefit levels and distribution",
    ]

    def formula(spm_unit, period, parameters):
        # Regular heating assistance available if LIHEAP eligible
        eligible = spm_unit("me_liheap_eligible", period)

        # Get benefit parameters
        p = parameters(period).gov.states.me.liheap.benefit_amounts
        min_benefit = p.benefit_min
        max_benefit = p.benefit_max

        # Benefit calculation factors from documentation:
        # 1. Household size: Larger households may receive higher benefits
        # 2. Household income: Lower income households receive higher benefits
        # 3. Energy burden: Cost of energy relative to household income

        income = spm_unit("me_liheap_income", period)
        household_size = spm_unit("spm_unit_size", period)

        # Get income threshold for household size
        p_thresholds = parameters(
            period
        ).gov.states.me.liheap.income_thresholds
        income_limit = select(
            [
                household_size == 1,
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
                household_size == 7,
                household_size == 8,
                household_size == 9,
                household_size == 10,
                household_size > 10,
            ],
            [
                p_thresholds.size_1,
                p_thresholds.size_2,
                p_thresholds.size_3,
                p_thresholds.size_4,
                p_thresholds.size_5,
                p_thresholds.size_6,
                p_thresholds.size_7,
                p_thresholds.size_8,
                p_thresholds.size_9,
                p_thresholds.size_10,
                p_thresholds.size_10 + (household_size - 10) * 2_000,
            ],
        )

        # Calculate base benefit using income-inverse relationship
        income_ratio = where(income_limit > 0, income / income_limit, 0)

        # Lower income = higher benefit percentage (inverse relationship)
        benefit_percentage = max_(0, 1 - income_ratio)

        # Household size factor - larger households get modestly higher benefits
        size_multiplier = (
            1 + (household_size - 1) * 0.05
        )  # 5% increase per additional person
        size_multiplier = min_(size_multiplier, 1.5)  # Cap at 50% increase

        # Calculate benefit amount
        benefit_range = max_benefit - min_benefit
        variable_benefit = benefit_range * benefit_percentage * size_multiplier
        total_benefit = min_benefit + variable_benefit

        # Ensure benefit stays within documented range
        final_benefit = min_(max_(total_benefit, min_benefit), max_benefit)

        return where(eligible, final_benefit, 0)
