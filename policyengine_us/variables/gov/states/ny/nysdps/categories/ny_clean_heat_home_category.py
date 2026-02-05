from policyengine_us.model_api import *


class HOMECategory(Enum):
    SINGLE = "Single Family Home"
    APARTMENT = "Apartment"


class ny_clean_heat_home_category(Variable):
    value_type = Enum
    entity = Household
    label = "New York Clean Heat home category"
    documentation = (
        "The home category for classifying clean heat program incentives"
    )
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    possible_values = HOMECategory
    default_value = HOMECategory.SINGLE
    defined_for = StateCode.NY
