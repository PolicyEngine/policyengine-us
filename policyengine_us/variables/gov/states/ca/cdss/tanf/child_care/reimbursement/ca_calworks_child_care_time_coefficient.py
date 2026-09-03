from policyengine_us.model_api import *


class ca_calworks_child_care_time_coefficient(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care time coefficient"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        time_category = person("ca_calworks_child_care_time_category", period)
        time_categories = time_category.possible_values
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        days_per_month = person("childcare_attending_days_per_month", period.this_year)
        days_per_week = person("childcare_days_per_week", period.this_year)
        # Weekly billing covers each week of the month; care reported through
        # either shared attendance input implies care every week.
        in_care = (days_per_week > 0) | (days_per_month > 0)
        weeks_per_month = in_care * WEEKS_IN_YEAR / MONTHS_IN_YEAR

        return select(
            [
                time_category == time_categories.HOURLY,
                time_category == time_categories.DAILY,
                time_category == time_categories.WEEKLY,
            ],
            [hours_per_day * days_per_month, days_per_month, weeks_per_month],
            default=1,  # Monthly.
        )
