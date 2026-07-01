from policyengine_us.model_api import *


class GACAPSProviderType(Enum):
    CENTER = "Center"
    FAMILY = "Family"
    INFORMAL = "Informal"


class ga_caps_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = GACAPSProviderType
    default_value = GACAPSProviderType.CENTER
    definition_period = MONTH
    label = "Georgia CAPS child care provider type"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixC-CAPS%20Reimbursement%20Rates.pdf#page=1"
