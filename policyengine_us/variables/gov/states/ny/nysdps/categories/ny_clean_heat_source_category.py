from policyengine_us.model_api import *


class HPCategory(Enum):
    ASHP = "air source heat pump"
    GSHP = "ground source heat pump"


class ny_clean_heat_source_category(Variable):
    value_type = Enum
    entity = Household
    label = "New York Clean Heat source category"
    documentation = (
        "The source category for classifying clean heat program incentives"
    )
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    possible_values = HPCategory
    default_value = HPCategory.GSHP
    defined_for = StateCode.NY
