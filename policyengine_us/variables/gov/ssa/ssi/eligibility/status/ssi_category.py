from policyengine_us.model_api import *


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

    def formula(person, period, parameters):
        is_blind = person("is_blind", period)
        is_aged = person("is_ssi_aged", period)
        is_disabled = person("is_ssi_disabled", period)

        # If multiple are true, pick whichever is your policy (often Blind overrides Aged, or we do a priority).
        # Here's a simple approach: blind > aged > disabled, or pick the first that's true:
        return select(
            [is_blind, is_aged, is_disabled],
            [SSICategory.BLIND, SSICategory.AGED, SSICategory.DISABLED],
            default=SSICategory.NONE,
        )
