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
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.income_disregard
        gross_income = person("ma_tcap_gross_earned_income", period)
        # monthly $200 work related expenses deduction if employed
        work_related_expenses_deduction = person(
            "ma_tafdc_work_related_expense_deduction", period
        )
        adjusted_monthly_income = (
            max_(gross_income - work_related_expenses_deduction, 0)
            / MONTHS_IN_YEAR
        )
        income_after_flat_disregard = max_(
            adjusted_monthly_income - p.flat,
            0,
        )
        # A percentage disregard is applied for the first 4 months in addition to the continuous flat disregard.
        percentage_disregard = max_(
            income_after_flat_disregard
            * p.percentage.rate
            * p.percentage.months,
            0,
        )
        return max_(
            income_after_flat_disregard - percentage_disregard,
            0,
        )
