from openfisca_us.model_api import *


class is_hud_elderly_disabled_family(Variable):
    value_type = bool
    entity = SPMUnit
    label = "HUD elderly or disabled family"
    unit = USD
    documentation = (
        "Whether an SPM unit is deemed elderly or disabled for HUD purposes"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.611"

    def formula(spm_unit, period, parameters):
        hud = parameters(period).hud
        person = spm_unit.members
        elderly = person("age", period) >= hud.elderly_age_threshold
        disabled = person("is_disabled", period)
        child = person("is_child", period)
        elderly_disabled_adult = (elderly | disabled) & ~child
        # Simplify to having any elderly or disabled adults.
        # Actual rule only applies to head of household or spouse.
        return spm_unit.any(elderly_disabled_adult)
