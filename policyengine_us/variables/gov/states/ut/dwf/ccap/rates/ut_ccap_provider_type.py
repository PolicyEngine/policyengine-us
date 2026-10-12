from policyengine_us.model_api import *


class UTCCAPProviderType(Enum):
    LICENSE_EXEMPT_HOME = "License-exempt home (family, friend, and neighbor)"
    LICENSED_COMMERCIAL_PRESCHOOL = "Licensed commercial preschool"
    LICENSE_EXEMPT_CENTER = "License-exempt center or residential certificate"
    LICENSED_FAMILY_HOME = "Licensed family home"
    LICENSED_CENTER = "Licensed center"


class ut_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = UTCCAPProviderType
    default_value = UTCCAPProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Utah CCAP child care provider type"
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/occ/provider/table30824.pdf",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-713",
    )
