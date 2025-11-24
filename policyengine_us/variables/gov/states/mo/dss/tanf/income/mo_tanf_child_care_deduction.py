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

        # Count children under age 2 and age 2+
        is_under_two = age < p.age_threshold
        is_two_and_over = (age >= p.age_threshold) & (age < 18)

        count_under_two = spm_unit.sum(is_under_two)
        count_two_and_over = spm_unit.sum(is_two_and_over)

        deduction_under_two = count_under_two * p.under_age_two
        deduction_two_and_over = count_two_and_over * p.age_two_and_over

        return deduction_under_two + deduction_two_and_over
