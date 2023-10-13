from policyengine_us.model_api import *


class CaChildCareServiceCategory(Enum):
    FULL_TIME = "Full time"
    PART_TIME = "Part time"


class ca_child_care_service_category(Variable):
    value_type = Enum
    possible_values = CaChildCareServiceCategory
    default_value = CaChildCareServiceCategory.FULL_TIME
    entity = Person
    label = "California CalWORKs Child Care service category"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.child_care.child_care_time.weekly_care.weekly_child_care_hours
        weekly_hours = person("childcare_hours_per_week", period)
        time_category = person("ca_child_care_time_category", period)
        time_categories = time_category.possible_values
        service_category = select(
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
            [
                CaChildCareServiceCategory.PART_TIME,
                CaChildCareServiceCategory.FULL_TIME,
                CaChildCareServiceCategory.PART_TIME,
                CaChildCareServiceCategory.FULL_TIME,
                CaChildCareServiceCategory.PART_TIME,
                CaChildCareServiceCategory.FULL_TIME,
            ],
        )

        return service_category
