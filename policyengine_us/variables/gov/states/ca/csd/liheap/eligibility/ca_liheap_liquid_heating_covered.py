from policyengine_us.model_api import *


class ca_liheap_liquid_heating_covered(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP ordinary liquid heating policy coverage, not eligibility"
    defined_for = StateCode.CA
    reference = (
        # PDF pages 185-188
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=185",
        # PDF pages 191,233-234
        "https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=191",
    )

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        liquid_heat = (heating_type == types.PROPANE) | (heating_type == types.FUEL_OIL)
        # Currently Madera only. A false result means the ordinary liquid
        # component is unsupported, including zero-income and over-100% burden.
        return liquid_heat & (spm_unit("ca_liheap_energy_burden_group", period) > 0)
