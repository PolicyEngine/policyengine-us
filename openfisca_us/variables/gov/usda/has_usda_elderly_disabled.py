from openfisca_us.model_api import *


class has_usda_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Whether the SPM unit has a person who meets USDA definitions of elderly or disabled"
    label = "Has USDA elderly or disabled people"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("is_usda_elderly", period)
        disabled = person("is_usda_disabled", period)
        return spm_unit.any(elderly | disabled)
