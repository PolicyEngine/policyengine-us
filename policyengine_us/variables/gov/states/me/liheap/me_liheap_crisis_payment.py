from policyengine_us.model_api import *


class me_liheap_crisis_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine LIHEAP crisis assistance payment"
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = [
        "docs/agents/sources/me-liheap/benefit_calculation.md",
        "docs/agents/sources/me-liheap/maine_liheap_overview.md",
        "42 U.S.C. § 8624(b)(2) - Crisis assistance benefit calculation",
    ]

    def formula(spm_unit, period, parameters):
        # Crisis assistance only available if crisis eligible
        crisis_eligible = spm_unit("me_liheap_crisis_eligible", period)

        # Get crisis assistance parameters
        p = parameters(period).gov.states.me.liheap.benefit_amounts
        max_crisis_benefit = p.crisis_max

        # Crisis benefit calculation - documentation indicates:
        # "Benefits vary inversely with income within eligibility range"
        # "Households at lower income levels receive higher benefit amounts"

        income = spm_unit("me_liheap_income", period.this_year)
        household_size = spm_unit("spm_unit_size", period.this_year)

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

        # Calculate benefit based on income as percentage of limit
        # Lower income = higher percentage of maximum benefit
        income_ratio = where(income_limit > 0, income / income_limit, 0)

        # Inverse relationship: lower income ratio = higher benefit percentage
        benefit_percentage = max_(0, 1 - income_ratio)

        # Calculate crisis payment
        crisis_payment = max_crisis_benefit * benefit_percentage

        return where(crisis_eligible, crisis_payment, 0)
