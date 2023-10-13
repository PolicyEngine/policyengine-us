from policyengine_us.model_api import *


class ca_child_care_time_coefficient(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care hours per month"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        time_category = person("ca_child_care_time_category", period)
        time_categories = time_category.possible_values
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_month = person("ca_child_care_days_per_month", period)
        weeks_per_month = person("ca_child_care_weeks_per_month", period)

        return select(
            [
                time_category == time_categories.HOURLY,
                time_category == time_categories.DAILY,
                time_category == time_categories.WEEKLY,
                time_category == time_categories.MONTHLY,
            ],
            [
                hours_per_day * days_per_month,
                days_per_month,
                weeks_per_month,
                1,
            ],
        )
