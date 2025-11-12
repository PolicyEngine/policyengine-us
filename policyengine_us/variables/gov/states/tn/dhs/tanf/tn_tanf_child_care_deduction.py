from policyengine_us.model_api import *


class tn_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF child care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "Tennessee TANF State Plan 2024-2027",
        "https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Tennessee.pdf",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        age = person("age", period)
        p = parameters(
            period
        ).gov.states.tn.dhs.tanf.income.deductions.child_care_deduction
        # Calculate deduction per child based on age
        deduction_per_child = p.calc(age)
        return spm_unit.sum(deduction_per_child)
