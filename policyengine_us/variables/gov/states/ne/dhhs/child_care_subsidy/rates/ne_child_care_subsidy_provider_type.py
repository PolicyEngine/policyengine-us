from policyengine_us.model_api import *


class NEChildCareSubsidyProviderType(Enum):
    HOME_I_II = "Licensed family child care home I or II"
    CENTER = "Licensed child care center"
    LICENSE_EXEMPT_FAMILY_HOME = "License-exempt family child care home"
    LICENSE_EXEMPT_IN_HOME = "License-exempt in-home provider"
    NONE = "No provider reported"


class ne_child_care_subsidy_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NEChildCareSubsidyProviderType
    # Defaults to the licensed-center category so survey and microdata
    # households without provider detail flow through the rate matrix path.
    default_value = NEChildCareSubsidyProviderType.CENTER
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy provider type"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=17",
        "https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf",
    )
