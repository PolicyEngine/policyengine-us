from policyengine_us.model_api import *


class ma_tafdc_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to immigration status"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-400"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        immigration_status = spm_unit.members("immigration_status", period)
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        return spm_unit.any(~undocumented)
