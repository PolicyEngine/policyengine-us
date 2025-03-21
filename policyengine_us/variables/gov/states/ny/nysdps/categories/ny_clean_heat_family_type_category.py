from policyengine_us.model_api import *


class FAMCategory(Enum):
    RESIDENTIAL = "Residential"
    MULTIFAMILY = "Multifamily"


class ny_clean_heat_family_type_category(Variable):
    value_type = Enum
    entity = Household
    label = "New York Clean Heat family type category"
    documentation = "The family type category for classifying clean heat program incentives"
    definition_period = YEAR
    possible_values = FAMCategory
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    default_value = FAMCategory.MULTIFAMILY
    defined_for = StateCode.NY
