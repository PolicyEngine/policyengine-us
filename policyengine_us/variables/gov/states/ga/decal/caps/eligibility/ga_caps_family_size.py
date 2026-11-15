from policyengine_us.model_api import *


class ga_caps_family_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Georgia CAPS family unit size"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27"

    def formula(spm_unit, period, parameters):
        # CAPS/00-5, 5.4.1: each child in DFCS custody forms a family unit of one, so
        # the foster family's own unit leaves those children out.
        size = spm_unit("spm_unit_size", period.this_year)
        return size - add(spm_unit, period, ["is_in_foster_care"])
