from policyengine_us.model_api import *


class has_md_elderly(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Has MD elderly people"
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("is_md_elderly", period)
        return spm_unit.any(elderly)
