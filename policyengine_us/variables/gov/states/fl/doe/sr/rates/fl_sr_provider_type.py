from policyengine_us.model_api import *


class FLSRProviderType(Enum):
    LICENSED_EXEMPT = "Licensed/Exempt"
    LICENSED_FAMILY_CHILD_CARE_HOME = "Licensed Family Child Care Home"
    REGISTERED_FAMILY_CHILD_CARE_HOME = "Registered Family Child Care Home"


class fl_sr_provider_type(Variable):
    value_type = Enum
    possible_values = FLSRProviderType
    default_value = FLSRProviderType.LICENSED_EXEMPT
    entity = Person
    definition_period = MONTH
    label = "Florida School Readiness child care provider type"
    reference = "https://flrules.elaws.us/fac/6m-4.500"
    # Provider type of the child's School Readiness child care provider, used to
    # select the maximum reimbursement rate; defaults to the licensed/exempt
    # (center) rate column.
