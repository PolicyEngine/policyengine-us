from policyengine_us.model_api import *


class ny_clean_heat_equipment_unit(Variable):
    value_type = int
    entity = Household
    label = "Number of qualified heat pump equipment units installed."
    documentation = "Equipment units must be of eligible technology categories and meet rating/specification requirements outlined in program manuals."
    unit = "unit"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=11"  # (2.1.1)
