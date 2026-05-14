from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ga.decal.caps.payment.ga_caps_provider_type import (
    GACAPSProviderType,
)


class ga_caps_maximum_weekly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Georgia CAPS maximum weekly benefit per child"
    definition_period = MONTH
    defined_for = "ga_caps_eligible_child"
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixC-CAPS%20Reimbursement%20Rates.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.rates
        zone = person.household("ga_caps_zone", period)
        age_group = person("ga_caps_age_group", period)
        care_type = person("ga_caps_care_type", period)
        provider_type = person("ga_caps_provider_type", period)

        center_rate = p.center[zone][age_group][care_type]
        family_rate = p.family[zone][age_group][care_type]
        informal_rate = p.informal[zone][age_group][care_type]

        rate = select(
            [
                provider_type == GACAPSProviderType.CENTER,
                provider_type == GACAPSProviderType.FAMILY,
                provider_type == GACAPSProviderType.INFORMAL,
            ],
            [center_rate, family_rate, informal_rate],
            default=center_rate,
        )

        # Part-time rates are daily; convert to weekly using days per week.
        is_part_time = care_type == care_type.possible_values.PART_TIME
        days_per_week = person("childcare_days_per_week", period.this_year)
        return where(is_part_time, rate * days_per_week, rate)
