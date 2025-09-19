from policyengine_us.model_api import *


class ny_clean_heat_project_cost(Variable):
    value_type = float
    entity = Household
    label = "New York Clean Heat project cost"
    documentation = (
        "The project cost for purchasing and installing a heat pump"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY
