from policyengine_us.model_api import *


class MECCAPProviderType(Enum):
    LICENSED_CENTER = "Licensed Child Care Center"
    LICENSED_FAMILY = "Licensed Family Child Care"
    LICENSE_EXEMPT = "License-Exempt Child Care"


class me_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MECCAPProviderType
    default_value = MECCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.ME
    label = "Maine CCAP child care provider type"
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=25"
