from policyengine_us.model_api import *


class CaCalworksChildCareTimeCategory(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class ca_calworks_child_care_time_category(Variable):
    value_type = Enum
    possible_values = CaCalworksChildCareTimeCategory
    default_value = CaCalworksChildCareTimeCategory.WEEKLY
    entity = Person
    label = "California CalWORKs Child Care time category"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/regional-market-rate-ceilings.html"
    # Depends on hours of care received per day or week.
    # We do not currently model this.
