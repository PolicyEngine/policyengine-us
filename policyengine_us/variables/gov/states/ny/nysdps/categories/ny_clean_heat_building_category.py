from policyengine_us.model_api import *


class BUILDCategory(Enum):
    NEW = "New Construction"
    EXISTING = "Existing Building"


class ny_clean_heat_building_category(Variable):
    value_type = Enum
    entity = Household
    label = "New York Clean Heat building category"
    documentation = (
        "The building category for classifying clean heat program incentives"
    )
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=13"
    possible_values = BUILDCategory
    default_value = BUILDCategory.NEW
    defined_for = StateCode.NY
