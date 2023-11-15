from policyengine_us.model_api import *


class CaCalworksChildCareServiceCategory(Enum):
    FULL_TIME = "Full time"
    PART_TIME = "Part time"


class ca_calworks_child_care_service_category(Variable):
    value_type = Enum
    possible_values = CaCalworksChildCareServiceCategory
    default_value = CaCalworksChildCareServiceCategory.FULL_TIME
    entity = Person
    label = "California CalWORKs Child Care service category"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.child_care_time.weekly_care
        weekly_hours = person("childcare_hours_per_week", period)
        time_category = person("ca_calworks_child_care_time_category", period)
        time_categories = time_category.possible_values
        return select(
            [
                (time_category == time_categories.HOURLY),
                (time_category == time_categories.DAILY),
                (time_category == time_categories.WEEKLY)
                & (weekly_hours < p.weekly_child_care_hours_threshold),
                (time_category == time_categories.WEEKLY)
                & (weekly_hours >= p.weekly_child_care_hours_threshold),
                (time_category == time_categories.MONTHLY)
                & (weekly_hours < p.weekly_child_care_hours_threshold),
                (time_category == time_categories.MONTHLY)
                & (weekly_hours >= p.weekly_child_care_hours_threshold),
            ],
            [
                CaCalworksChildCareServiceCategory.PART_TIME,
                CaCalworksChildCareServiceCategory.FULL_TIME,
                CaCalworksChildCareServiceCategory.PART_TIME,
                CaCalworksChildCareServiceCategory.FULL_TIME,
                CaCalworksChildCareServiceCategory.PART_TIME,
                CaCalworksChildCareServiceCategory.FULL_TIME,
            ],
        )
