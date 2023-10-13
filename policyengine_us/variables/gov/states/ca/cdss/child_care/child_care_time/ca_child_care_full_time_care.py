from policyengine_us.model_api import *


class ca_child_care_full_time_care(Variable):
    value_type = bool
    entity = Person
    label = "California CalWORKs Child Care full time"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.child_care.child_care_time.weekly_care.weekly_child_care_hours
        weekly_hours = person("childcare_hours_per_week", period)
        time_category = person("ca_child_care_time_category", period)
        time_categories = time_category.possible_values
        is_full_time = select(
            [
                (time_category == time_categories.HOURLY),
                (time_category == time_categories.DAILY),
                (time_category == time_categories.WEEKLY) & (weekly_hours < p),
                (time_category == time_categories.WEEKLY)
                & (weekly_hours >= p),
                (time_category == time_categories.MONTHLY)
                & (weekly_hours < p),
                (time_category == time_categories.MONTHLY)
                & (weekly_hours >= p),
            ],
            [False, True, False, True, False, True],
        )

        return is_full_time
