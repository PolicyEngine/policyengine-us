from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class il_ihwap_hhs_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois IHWAP State Median Income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/homeweatherization.html"
    )

    def formula(spm_unit, period, parameters):
        # IL IHWAP Program Year N uses SMI from October 1 of year N-1
        # e.g., PY2026 uses SMI effective 2025-10-01
        prior_october = f"{period.start.year - 1}-10-01"

        size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code_str", period)

        return smi(size, state, prior_october, parameters)
