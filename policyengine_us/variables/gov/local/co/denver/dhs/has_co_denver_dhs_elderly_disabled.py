from policyengine_us.model_api import *


class has_co_denver_dhs_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Whether the SPM unit has a person who meets Denver DHS definitions of elderly or disabled"
    label = "Has Denver DHS elderly or disabled people"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("is_co_denver_dhs_elderly", period)
        disabled = person("is_disabled", period)
        return spm_unit.any(elderly | disabled)
