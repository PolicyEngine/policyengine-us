from policyengine_us.model_api import *


class MICCAPProviderType(Enum):
    CENTER = "Child care center"
    FAMILY_HOME = "Group and family child care home"
    LICENSE_EXEMPT = "License-exempt related and unrelated"


class mi_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MICCAPProviderType
    default_value = MICCAPProviderType.CENTER
    definition_period = MONTH
    label = "Michigan CDC child care provider type"
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=4"
    )
