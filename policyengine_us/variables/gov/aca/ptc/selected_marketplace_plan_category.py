from policyengine_us.model_api import *


class MarketplacePlanCategory(Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"


class selected_marketplace_plan_category(Variable):
    value_type = Enum
    possible_values = MarketplacePlanCategory
    default_value = MarketplacePlanCategory.SILVER
    entity = TaxUnit
    label = "Selected Marketplace plan category"
    definition_period = YEAR
