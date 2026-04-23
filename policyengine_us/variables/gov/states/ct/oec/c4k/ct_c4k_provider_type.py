from policyengine_us.model_api import *


class CTC4KProviderType(Enum):
    CENTER = "Centers/Group Homes/School Programs"
    FAMILY = "Licensed Family Child Care Homes"
    RELATIVE = "Unlicensed Relative Care"
    RECREATIONAL = "Recreational Programs (Summer)"


class ct_c4k_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = CTC4KProviderType
    default_value = CTC4KProviderType.CENTER
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids provider type"
    reference = "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/"
