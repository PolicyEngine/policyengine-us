from policyengine_us.model_api import *


class ny_clean_heat_heating_capacity(Variable):
    value_type = float
    entity = Household
    label = "System's qualified max heating capacity"
    documentation = "System's heating capacity that meets certification and system sizing requirements per program manuals."
    unit = "BTU/h"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=28"  # (3.3)(3.4)(3.7)
