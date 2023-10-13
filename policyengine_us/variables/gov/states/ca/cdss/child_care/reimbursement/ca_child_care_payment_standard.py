from policyengine_us.model_api import *


class ca_child_care_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Payment Standard"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.child_care.rate_ceilings.standard
        person = spm_unit.members
        provider = person("ca_child_care_provider_category", period)
        time_category = person("ca_child_care_time_category", period)
        time_categories = time_category.possible_values
        is_full_time = person("ca_child_care_full_time_care", period)
        service_type = where(is_full_time == True, "full_time", "part_time")

        hours_per_day = person("childcare_hours_per_day", period)
        days_per_month = person("ca_child_care_days_per_month", period)
        hours_per_week = person("childcare_hours_per_week", period)
        weeks_per_month = person("ca_child_care_weeks_per_month", period)

        hours_per_month = select(
            [
                (time_category == time_categories.HOURLY)
                | (time_category == time_categories.DAILY),
                (time_category == time_categories.WEEKLY)
                | (time_category == time_categories.MONTHLY),
            ],
            [hours_per_day * days_per_month, hours_per_week * weeks_per_month],
        )

        child = person("is_child", period)
        persons_age = person("age", period)
        child_payment = 0
        for pro, tim, ser, per, chi in zip(
            provider, time_category, service_type, persons_age, child
        ):
            child_payment += p[pro][tim][ser].calc(per)

        return child_payment
