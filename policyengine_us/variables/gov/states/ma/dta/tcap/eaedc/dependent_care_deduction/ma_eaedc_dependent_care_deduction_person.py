from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Massachusetts EAEDC dependent care deduction for each person"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275"  # (A)
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        dependent = person("ma_eaedc_eligible_dependent", period)
        total_weekly_hours = person.spm_unit.sum(
            person("weekly_hours_worked", period.this_year)
        )
        age = person("monthly_age", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.deductions.dependent_care_expenses
        young_child = age < p.young_child_age_threshold
        amount = where(
            young_child,
            p.amount.younger.calc(total_weekly_hours),
            p.amount.older.calc(total_weekly_hours),
        )
        total_amount = amount * dependent
        care_expenses = person("pre_subsidy_childcare_expenses", period)
        return min_(total_amount, care_expenses)
