from policyengine_us.model_api import *


class UtilityProvider(Enum):
    CH = "Central Hudson"
    NG = "National Grid"
    SEGRGE = "NYSEG/RG&E"
    OR = "Orange & Rockland"


class utility_provider(Variable):
    value_type = Enum
    entity = Household
    label = "NYS Energy Company/Utility Provider"
    definition_period = YEAR
    defined_for = StateCode.NY
    possible_values = UtilityProvider
    default_value = UtilityProvider.CH
