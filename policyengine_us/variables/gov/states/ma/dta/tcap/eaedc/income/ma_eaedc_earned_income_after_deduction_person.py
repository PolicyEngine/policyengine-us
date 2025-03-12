from policyengine_us.model_api import *


class ma_eaedc_earned_income_after_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income after deduction for each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.deductions
        gross_earned_income = person("ma_eaedc_total_earned_income", period)
        monthly_income = gross_earned_income / MONTHS_IN_YEAR
        # monthly $200 work related expenses deduction if employed
        is_employed = gross_earned_income > 0
        adjusted_monthly_income = max_(
            monthly_income - p.work_related_expenses * is_employed, 0
        )
        # Compute earned income after disregard, first 4 months has flat $30 then 1/3 disregard, the rest 8 months has flat $30 deduction.
        first_four_months_income = max_(
            (adjusted_monthly_income - p.income_disregard.flat)
            * (1 - p.income_disregard.percentage.rate)
            * p.income_disregard.percentage.months,
            0,
        )
        remaining_months = max_(
            MONTHS_IN_YEAR - p.income_disregard.percentage.months, 0
        )
        reduced_remaining_monthly_income = max_(
            adjusted_monthly_income - p.income_disregard.flat,
            0,
        )

        remaining_income = reduced_remaining_monthly_income * remaining_months

        return first_four_months_income + remaining_income
