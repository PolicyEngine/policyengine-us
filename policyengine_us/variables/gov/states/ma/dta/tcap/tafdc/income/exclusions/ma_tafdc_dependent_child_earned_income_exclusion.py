from policyengine_us.model_api import *


class ma_tafdc_dependent_child_earned_income_exclusion(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC dependent child" " earned income exclusion"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Section (U): Earned income of a dependent child
        # under 16, or 16+ if a full-time student.
        age = person("age", period.this_year)
        p = parameters(period).gov.states.ma.dta.tcap.tafdc
        threshold = p.income.noncountable.child_earned_income
        age_threshold = threshold.age_threshold
        is_student = person("is_full_time_student", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        eligible = is_dependent & (
            (age < age_threshold) | ((age >= age_threshold) & is_student)
        )
        gross_earned = person("ma_tcap_gross_earned_income", period)
        return where(eligible, gross_earned, 0)
