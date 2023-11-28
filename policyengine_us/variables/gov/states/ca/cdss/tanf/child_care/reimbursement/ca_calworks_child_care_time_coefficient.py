from policyengine_us.model_api import *


class ca_calworks_child_care_time_coefficient(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care hours per month"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        time_category = person("ca_calworks_child_care_time_category", period)
        time_categories = time_category.possible_values
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_month = person(
            "ca_calworks_child_care_days_per_month", period
        )
        weeks_per_month = person(
            "ca_calworks_child_care_weeks_per_month", period
        )

        return select(
            [
                time_category == time_categories.HOURLY,
                time_category == time_categories.DAILY,
                time_category == time_categories.WEEKLY,
            ],
            [hours_per_day * days_per_month, days_per_month, weeks_per_month],
            default=1,  # Monthly.
        )
