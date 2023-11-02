from policyengine_us.model_api import *


class CaChildCareTimeCategory(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class ca_child_care_time_category(Variable):
    value_type = Enum
    possible_values = CaChildCareTimeCategory
    default_value = CaChildCareTimeCategory.WEEKLY
    entity = Person
    label = "California CalWORKs Child Care time category"
    definition_period = YEAR
    defined_for = StateCode.CA
