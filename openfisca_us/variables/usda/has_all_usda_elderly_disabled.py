from openfisca_us.model_api import *


class has_all_usda_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Whether the SPM unit's members all meet USDA definitions of elderly or disabled"
    label = "Has all USDA elderly or disabled people"
    # NB: This isn't used in SNAP directly, but it is used for BBCE (TANF).

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("is_usda_elderly", period)
        disabled = person("is_usda_disabled", period)
        return spm_unit.all(elderly | disabled)
