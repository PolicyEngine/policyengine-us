from policyengine_us.model_api import *


class mo_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF child care cost deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.child_care_deduction
        person = spm_unit.members
        age = person("age", period.this_year)
        is_under_two = age < p.age_threshold
        is_two_and_over = (age >= p.age_threshold) & (age < p.max_age)
        under_two_deduction = (
            spm_unit.sum(is_under_two) * p.amount_under_age_two
        )
        two_and_over_deduction = (
            spm_unit.sum(is_two_and_over) * p.amount_age_two_and_over
        )
        return under_two_deduction + two_and_over_deduction
