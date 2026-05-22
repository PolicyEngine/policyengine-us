from policyengine_us.model_api import *


class MTSSPPaymentCategory(Enum):
    ASSISTED_LIVING_OR_GROUP_OR_COMMUNITY_HOME = (
        "Personal care, group home, or community home"
    )
    FOSTER_CARE = "Foster care home"
    TRANSITIONAL_LIVING = "Transitional living services"
    NONE = "None"


class mt_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Montana SSP payment category"
    definition_period = MONTH
    defined_for = StateCode.MT
    possible_values = MTSSPPaymentCategory
    default_value = MTSSPPaymentCategory.NONE
    reference = (
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-103",
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-104",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
    )
