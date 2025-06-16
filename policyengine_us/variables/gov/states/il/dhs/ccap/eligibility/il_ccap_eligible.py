from policyengine_us.model_api import *


class il_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Child Care Assistance Program (CCAP)"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=104995"

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("il_ccap_income_eligible", period)
        has_eligible_child = (
            add(spm_unit, period, ["il_ccap_eligible_child"]) > 0
        )
        parent_meets_working_requirements = spm_unit(
            "il_ccap_parent_meets_working_requirements", period
        )
        return (
            income_eligible
            & has_eligible_child
            & parent_meets_working_requirements
        )
