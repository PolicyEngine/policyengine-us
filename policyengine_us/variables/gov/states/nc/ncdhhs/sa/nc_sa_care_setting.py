from policyengine_us.model_api import *


class NCSACareSetting(Enum):
    ADULT_CARE_HOME = "Approved basic residential care"
    SPECIAL_CARE_UNIT = "Approved enhanced special care unit"
    IN_HOME = "Approved basic in-home care"
    IN_HOME_ENHANCED = "Approved enhanced in-home care"
    NONE = "No approved Special Assistance care setting"


class nc_sa_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "North Carolina Special Assistance certified care setting"
    definition_period = MONTH
    possible_values = NCSACareSetting
    default_value = NCSACareSetting.NONE
    documentation = "A positive category indicates an approved placement or in-home service plan with a valid FL-2, satisfaction of the state residency waiting period or exception, pursuit of other benefits, and no conflicting PACE or waiver enrollment. Enhanced settings require the qualifying dementia diagnosis. A blind child requires a certified specialized community residential center. Put spouses who no longer live in the same household, such as a facility resident whose spouse stays at home, in separate marital units from the month after they stop living together, so that SSI and Special Assistance treat each spouse as an individual. Keep one marital unit for the month of entry and for a temporary absence."
    reference = (
        # PDF pages 6-7, 10, 204-205
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=6",
        # PDF pages 14-17
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=14",
    )
