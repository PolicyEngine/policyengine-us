from openfisca_us.model_api import *


class SSICategory(Enum):
    AGED = "Aged"
    BLIND = "Blind"
    DISABLED = "Disabled"
    NONE = "None"


class ssi_category(Variable):
    value_type = Enum
    entity = Person
    label = "SSI category"
    definition_period = YEAR
    possible_values = SSICategory
    default_value = SSICategory.NONE
