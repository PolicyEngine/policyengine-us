from policyengine_us.model_api import *


class pa_tanf_has_pregnant_member(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF unit has pregnant member"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 105, Section 105.2 - TANF Categorical Requirements"
    documentation = "The SPM unit includes at least one pregnant woman. Pregnant women with no other dependent children are eligible for PA TANF (Category C). http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_pregnant = person("is_pregnant", period)

        return spm_unit.any(is_pregnant)
