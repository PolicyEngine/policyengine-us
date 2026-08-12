from policyengine_us.model_api import *


class SDCCAProviderType(Enum):
    FAMILY_DAY_CARE = "Family day care"
    LICENSED_CENTER = "Licensed center or school age program"
    INFORMAL = "Informal, in-home, or relative"


class sd_cca_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = SDCCAProviderType
    default_value = SDCCAProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA child care provider type"
    reference = "https://dss.sd.gov/docs/childcare/assistance/CCA_Weekly_Reimbursement_Rates.pdf"
