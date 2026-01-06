from policyengine_us.model_api import *


class sc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned.disregard
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        monthly_income = gross_earned_income / MONTHS_IN_YEAR
        # Compute earned income after disregard, first four months has 50% disregard, the rest has $100 deduction.
        first_four_months_income = (
            monthly_income * p.percentage.rate * p.percentage.months
        )
        remaining_months = max_(MONTHS_IN_YEAR - p.percentage.months, 0)
        reduced_remaining_monthly_income = max_(monthly_income - p.amount, 0)
        remaining_income = reduced_remaining_monthly_income * remaining_months
        return first_four_months_income + remaining_income
