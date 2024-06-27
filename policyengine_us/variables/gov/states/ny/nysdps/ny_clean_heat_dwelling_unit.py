from policyengine_us.model_api import *


class ny_clean_heat_dwelling_unit(Variable):
    value_type = int
    entity = TaxUnit
    label = "Dwelling Unit"
    documentation = "The number of dwelling unit"
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=13"
    defined_for = StateCode.NY