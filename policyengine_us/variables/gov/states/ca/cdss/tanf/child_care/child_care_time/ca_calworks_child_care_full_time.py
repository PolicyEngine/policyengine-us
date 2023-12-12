from policyengine_us.model_api import *


class ca_calworks_child_care_full_time(Variable):
    value_type = bool
    entity = Person
    label = "Whether a child is classified as receiving full-time care for CalWORKs Child Care"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.child_care_time.weekly_care
        weekly_hours = person("childcare_hours_per_week", period)
        time_category = person("ca_calworks_child_care_time_category", period)
        # Hourly is never full-time.
        # Daily is always full-time.
        # Weekly and monthly depend on meeting the weekly hours threshold.
        time_categories = time_category.possible_values
        meets_hours_threshold = (
            weekly_hours >= p.weekly_child_care_hours_threshold
        )
        weekly_or_monthly = (time_category == time_categories.WEEKLY) | (
            time_category == time_categories.MONTHLY
        )
        weekly_or_monthly_full_time = weekly_or_monthly & meets_hours_threshold
        daily = time_category == time_categories.DAILY
        return daily | weekly_or_monthly_full_time
