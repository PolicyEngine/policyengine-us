from policyengine_us.model_api import *


class CaCalworksChildCareFactorCategory(Enum):
    STANDARD = "Standard Rate Ceilings"
    EVENING_AND_WEEKEND_I = "Evening/Weekend Care Rate Ceilings (50% or more of time)"
    EVENING_AND_WEEKEND_II = (
        "Evening/Weekend Care Rate Ceilings (at least 10% but less than 50% of time)"
    )
    EXCEPTIONAL_NEEDS = "Exceptional Needs Care Rate Ceilings"
    SEVERELY_DISABLED = "Severely Disabled Care Rate Ceilings"


class ca_calworks_child_care_factor_category(Variable):
    value_type = Enum
    possible_values = CaCalworksChildCareFactorCategory
    default_value = CaCalworksChildCareFactorCategory.STANDARD
    entity = Person
    label = "California CalWORKs Child Care factor category"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/regional-market-rate-ceilings.html"
