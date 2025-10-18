"""
Connecticut TFA assistance unit size calculation.
"""

from policyengine_us.model_api import *


class ct_tfa_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Connecticut TFA assistance unit size"
    definition_period = YEAR
    defined_for = StateCode.CT
    documentation = (
        "The number of eligible members in the Connecticut TFA assistance unit, "
        "including dependent children under age 18 (or age 18 if enrolled in "
        "high school or vocational school full-time) and related adults or guardians."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026; "
        "Connecticut TFA Fact Sheet - Household Composition "
        "https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        # Count all persons in the SPM unit for TFA purposes
        # Note: In a more detailed implementation, this could exclude
        # certain ineligible household members based on specific rules
        return spm_unit.nb_persons()
