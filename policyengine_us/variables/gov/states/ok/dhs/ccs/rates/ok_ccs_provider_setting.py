from policyengine_us.model_api import *


class OKCCSProviderSetting(Enum):
    CHILD_CARE_CENTER = "Child care center"
    CHILD_CARE_HOME = "Child care home"
    IN_HOME = "In-home care"


class ok_ccs_provider_setting(Variable):
    value_type = Enum
    entity = Person
    possible_values = OKCCSProviderSetting
    default_value = OKCCSProviderSetting.CHILD_CARE_CENTER
    definition_period = MONTH
    label = "Oklahoma Child Care Subsidy provider setting"
    defined_for = StateCode.OK
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=1"
