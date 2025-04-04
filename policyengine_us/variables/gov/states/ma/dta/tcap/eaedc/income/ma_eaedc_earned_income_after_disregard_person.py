from policyengine_us.model_api import *


class ma_eaedc_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income after disregard for each person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.income_disregard
        gross_income = person("ma_tcap_gross_earned_income", period)
        # work_related_expenses_deduction = person(
        #     "ma_tafdc_work_related_expense_deduction", period
        # )
        income_after_work_related_expenses_deduction = max_(
            gross_income - 0, 0
        )
        income_after_flat_disregard = max_(
            income_after_work_related_expenses_deduction - p.flat,
            0,
        )
        percentage_disregard = income_after_flat_disregard * p.percentage.rate
        if period.start.month <= p.percentage.months:
            return max_(income_after_flat_disregard - percentage_disregard, 0)
        # A percentage disregard is applied for the first 4 months in addition to the continuous flat disregard.
        return income_after_flat_disregard
