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
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"
    # Depends on hours of care received per day or week.
    # We do not currently model this.
