from policyengine_us.model_api import *


class HIOSSCareFacilityType(Enum):
    COMMUNITY_CARE = "Community care foster family home"
    DOMICILIARY_CARE_I = "Domiciliary care facility with 5 or fewer residents"
    DOMICILIARY_CARE_II = "Domiciliary care facility with 6 or more residents"
    NONE = "Not in a qualifying care facility"


class hi_oss_care_facility_type(Variable):
    value_type = Enum
    entity = Person
    label = "Hawaii OSS care facility type"
    definition_period = MONTH
    defined_for = StateCode.HI
    possible_values = HIOSSCareFacilityType
    default_value = HIOSSCareFacilityType.NONE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415210SF"
