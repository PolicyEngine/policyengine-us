from policyengine_us.model_api import *


class ia_cca_has_special_needs_child(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa CCA family includes a child with special needs"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=1"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_eligible_child = person("ia_cca_eligible_child", period)
        is_disabled = person("is_disabled", period.this_year)
        return spm_unit.any(is_eligible_child & is_disabled)
