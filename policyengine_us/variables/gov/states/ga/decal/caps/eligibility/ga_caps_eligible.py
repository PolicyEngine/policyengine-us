from policyengine_us.model_api import *


class ga_caps_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        # PDF pages 27, 29
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # CAPS serves each child in DFCS custody as a family unit of one (CAPS/00-5,
        # 5.4.1; CAPS/00-7, 7.5) and the family's other children when the family
        # qualifies on its own.
        has_dfcs_custody_child = (
            add(spm_unit, period, ["ga_caps_dfcs_custody_child"]) > 0
        )
        return spm_unit("ga_caps_family_eligible", period) | has_dfcs_custody_child
