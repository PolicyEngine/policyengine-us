from policyengine_us.model_api import *


class SDSSPCareSetting(Enum):
    ASSISTED_LIVING = "Assisted living facility"
    ADULT_FOSTER_CARE = "Licensed adult foster care"
    NONE = "Not in assisted living or adult foster care"


class sd_ssp_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "South Dakota SSP assisted living or adult foster care setting"
    definition_period = MONTH
    defined_for = StateCode.SD
    possible_values = SDSSPCareSetting
    default_value = SDSSPCareSetting.NONE
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:12:14:02",
        "https://sdlegislature.gov/Rules/Administrative/67:46:03:03",
    )
    documentation = "Set for any assisted living or adult foster care resident, including residents on a Medicaid waiver or paying privately. ARSD 67:12:14:02(4) makes these residents ineligible for the independent living payment. Certified nonwaiver residents without a setting are treated as in assisted living."
