from policyengine_us.model_api import *


class ny_clean_heat_mmbtu(Variable):
    value_type = float
    entity = Household
    label = "New York Clean Heat MMBtu"
    documentation = "Million British Thermal Units"
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=13"
    defined_for = StateCode.NY
