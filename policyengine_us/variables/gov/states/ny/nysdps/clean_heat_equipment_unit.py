from policyengine_us.model_api import *


class clean_heat_equipment_unit(Variable):
    value_type = int
    entity = Household
    label = "Number of qualified heat pump equipment units installed."
    documentation = "Equipment units must be of eligible technology categories and meet rating/specification requirements outlined in program manuals."
    unit = unit # ?
    definition_period = YEAR
    defined_for = StateCode.NY # can we specify state and that it's defined for certain categories?
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf" # (2.1.1)