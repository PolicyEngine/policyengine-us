from policyengine_us.model_api import *


class is_hud_elderly_disabled_family(Variable):
    value_type = bool
    entity = SPMUnit
    label = "HUD elderly or disabled family"
    documentation = "Whether an SPM unit is deemed elderly or disabled for HUD purposes"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.611"

    def formula(spm_unit, period, parameters):
        hud = parameters(period).gov.hud
        person = spm_unit.members
        elderly = person("age", period) >= hud.elderly_age_threshold
        # 42 U.S.C. 1437a(b)(3)(E) defines a person with disabilities to
        # include anyone with a disability as defined in section 223 of the
        # Social Security Act (the SSDI standard), so the SSI/SSDI paths
        # qualify alongside the generic disability flag.
        disabled = (
            person("is_disabled", period)
            | person("is_ssi_disabled", period)
            | (person("social_security_disability", period) > 0)
        )
        child = person("is_child", period)
        elderly_disabled_adult = (elderly | disabled) & ~child
        # Simplify to having any elderly or disabled adults.
        # Actual rule only applies to head of household or spouse.
        return spm_unit.any(elderly_disabled_adult)
