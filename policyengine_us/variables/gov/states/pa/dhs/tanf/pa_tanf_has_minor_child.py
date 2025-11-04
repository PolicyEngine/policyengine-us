from policyengine_us.model_api import *


class pa_tanf_has_minor_child(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF unit has minor child"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 105, Section 105.2 - TANF Categorical Requirements"
    documentation = "The SPM unit includes at least one minor child as defined by Pennsylvania TANF categorical requirements. http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_minor_child = person("pa_tanf_is_minor_child", period)

        return spm_unit.any(is_minor_child)
