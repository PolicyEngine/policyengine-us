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
    documentation = "Provider type of the child's School Readiness child care provider, used to select the maximum reimbursement rate. Defaults to the licensed/exempt (center) rate column."
    reference = "https://www.flrules.org/gateway/RuleNo.asp?id=6M-4.500"
