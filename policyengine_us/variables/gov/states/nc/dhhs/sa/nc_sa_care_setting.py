from policyengine_us.model_api import *


class NCSACareSetting(Enum):
    NONE = "No approved Special Assistance care setting"
    ADULT_CARE_HOME = "Approved basic residential care"
    SPECIAL_CARE_UNIT = "Approved enhanced special care unit"
    IN_HOME = "Approved basic in-home care"
    IN_HOME_ENHANCED = "Approved enhanced in-home care"


class nc_sa_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "North Carolina Special Assistance certified care setting"
    definition_period = MONTH
    possible_values = NCSACareSetting
    default_value = NCSACareSetting.NONE
    documentation = "A positive category indicates an approved placement or in-home service plan with a valid FL-2, satisfaction of the state residency waiting period or exception, pursuit of other benefits, and no conflicting PACE or waiver enrollment. Enhanced settings require the qualifying dementia diagnosis. A blind child requires a certified specialized community residential center."
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf",
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf",
    )
