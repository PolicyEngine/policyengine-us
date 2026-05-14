from policyengine_us.model_api import *


class WICInfantFeedingCategory(Enum):
    AVERAGE = "Average"
    FULLY_FORMULA_FED = "Fully formula fed"
    PARTIALLY_BREASTFED = "Partially breastfed"
    FULLY_BREASTFED = "Fully breastfed"


class wic_infant_feeding_category(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    possible_values = WICInfantFeedingCategory
    default_value = WICInfantFeedingCategory.AVERAGE
    label = "WIC infant feeding category"
    documentation = "Infant feeding status used to assign WIC infant food packages"
    reference = "https://www.law.cornell.edu/cfr/text/7/246.10#e_1_ii"
