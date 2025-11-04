from policyengine_us.model_api import *


class pa_tanf_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF categorical eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 105, Section 105.2 - TANF Categorical Requirements"
    documentation = "The SPM unit meets Pennsylvania TANF categorical eligibility requirements by having either a minor child or a pregnant woman. http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"

    def formula(spm_unit, period, parameters):
        has_minor_child = spm_unit("pa_tanf_has_minor_child", period)
        has_pregnant = spm_unit("pa_tanf_has_pregnant_member", period)

        # Categorically eligible if unit has minor child OR pregnant woman
        return has_minor_child | has_pregnant
