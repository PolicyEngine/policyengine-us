from policyengine_us.model_api import *


class ny_clean_heat_project_cost(Variable):
    value_type = float
    entity = Household
    label = "Qualified heat pump installation project cost"
    documentation = "Qualified project cost for incentives includes equipment and labor costs only."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=64"  # (4.2)(4.3)(4.4)
