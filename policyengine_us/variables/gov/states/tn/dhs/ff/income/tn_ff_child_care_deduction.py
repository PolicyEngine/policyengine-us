from policyengine_us.model_api import *


class tn_ff_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First child care deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        age = person("age", period.this_year)
        p = parameters(
            period
        ).gov.states.tn.dhs.ff.income.deductions.child_care_deduction
        # Calculate deduction per child based on age
        deduction_per_child = p.calc(age)
        return spm_unit.sum(deduction_per_child)
