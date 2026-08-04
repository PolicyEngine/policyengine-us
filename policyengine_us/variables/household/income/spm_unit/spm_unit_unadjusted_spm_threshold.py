from policyengine_us.model_api import *
from spm_calculator.equivalence_scale import spm_equivalence_scale


class spm_unit_unadjusted_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit unadjusted SPM poverty threshold"
    documentation = "SPM poverty threshold before geographic adjustment."
    definition_period = YEAR
    unit = USD

    def formula_2015(spm_unit, period, parameters):
        reference_threshold = spm_unit(
            "spm_unit_reference_spm_threshold",
            period,
        )
        adults = spm_unit("spm_unit_count_adults", period)
        children = spm_unit("spm_unit_count_children", period)
        equivalence_scale = spm_equivalence_scale(adults, children)
        return reference_threshold * equivalence_scale
