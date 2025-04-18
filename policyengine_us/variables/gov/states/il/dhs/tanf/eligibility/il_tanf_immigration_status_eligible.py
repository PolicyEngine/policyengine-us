from policyengine_us.model_api import *


class il_tanf_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Illinois TANF based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.10"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        immigration_status = spm_unit.members("immigration_status", period)
        is_undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        return spm_unit.any(~is_undocumented)
