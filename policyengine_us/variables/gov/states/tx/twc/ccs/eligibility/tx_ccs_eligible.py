from policyengine_us.model_api import *


class tx_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-41"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        standard_requirements = spm_unit(
            "tx_ccs_meets_standard_family_requirements", period
        )
        person = spm_unit.members
        eligible_child = person("tx_ccs_eligible_child", period)
        has_eligible_child = spm_unit.any(eligible_child)
        authorized_child = person("tx_ccs_dfps_authorized", period) & eligible_child
        return (standard_requirements & has_eligible_child) | spm_unit.any(
            authorized_child
        )
