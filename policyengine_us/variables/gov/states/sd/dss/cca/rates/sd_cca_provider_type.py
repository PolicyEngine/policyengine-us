from policyengine_us.model_api import *


class SDCCAProviderType(Enum):
    FAMILY_DAY_CARE = "Family day care"
    LICENSED_CENTER = "Licensed center"
    INFORMAL = "Informal, in-home, or relative"
    BEFORE_AFTER_SCHOOL = "Licensed before-and-after-school program"


class sd_cca_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = SDCCAProviderType
    default_value = SDCCAProviderType.LICENSED_CENTER
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA child care provider type"
    documentation = "Records the provider category. The hourly schedule distinguishes licensed centers from before-and-after-school programs; the weekly schedule pays both from the licensed-center table."
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/CCA_Weekly_Reimbursement_Rates.pdf",
        "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Before_After_School_Programs.pdf",
    )
