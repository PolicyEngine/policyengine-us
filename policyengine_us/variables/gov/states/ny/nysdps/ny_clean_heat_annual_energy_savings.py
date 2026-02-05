from policyengine_us.model_api import *


class ny_clean_heat_annual_energy_savings(Variable):
    value_type = float
    entity = Household
    label = "Projected annual energy savings for heat pump installation"
    documentation = "Methodology for estimations of annual energy savings must follow the Technical Resource Manual or custom category engineering savings analysis guidelines."
    unit = "MMBtu"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=52"  # (3.8)(3.9)
