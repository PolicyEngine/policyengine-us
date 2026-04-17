from policyengine_us.model_api import *


class nm_works_countable_non_liquid_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works countable non-liquid resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0510.html",
        "https://www.hca.nm.gov/wp-content/uploads/TANF-Final-State-Plan-2024-to-2026.pdf#page=20",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # 8.102.510.9 and 8.102.510.10 NMAC make non-liquid resources a
        # program-specific concept: the home is excluded, and vehicles used for
        # transportation to work, school, or other daily living activities are
        # excluded. Current inputs do not distinguish exempt home value from
        # other real property, or exempt transportation vehicles from countable
        # recreational vehicles/equipment. Keep the state-specific concept in
        # policy code, but conservatively assign zero until those non-exempt
        # signals are modeled explicitly.
        return 0
