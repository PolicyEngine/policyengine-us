from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ms.dhs.ccpp.ms_ccpp_provider_type import (
    MSCCPPProviderType,
)


class ms_ccpp_maximum_weekly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Mississippi CCPP maximum weekly rate per child"
    definition_period = MONTH
    defined_for = "ms_ccpp_eligible_child"
    # 2024 Market Rate Survey, Table 1 (licensed center, p.9) and Table 2
    # (registered family home, p.10); operative "Current CCPP Rates" pp.9-10.
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2024/06/Mississippi-Child-Care-Market-Rate-Survey-2024.pdf#page=9"

    def formula(person, period, parameters):
        rates = parameters(period).gov.states.ms.dhs.ccpp.rates
        provider_type = person("ms_ccpp_provider_type", period)
        time_category = person("ms_ccpp_time_category", period)
        age_group = person("ms_ccpp_age_group", period)
        location = person.household("ms_ccpp_facility_location", period.this_year)

        is_center = provider_type == MSCCPPProviderType.CENTER

        # Standard rates by location, age band, and time category.
        center_rate = rates.center[location][age_group][time_category]
        family_home_rate = rates.family_home[location][age_group][time_category]
        standard_rate = where(is_center, center_rate, family_home_rate)

        # Special-needs (and in-home) children draw the flat all-ages
        # special-needs rate set; in-home care is paid the home-based rate.
        special_needs_center_rate = rates.special_needs_center[location][time_category]
        special_needs_home_rate = rates.special_needs_home[location][time_category]
        special_needs_rate = where(
            is_center, special_needs_center_rate, special_needs_home_rate
        )

        is_special_needs = person("is_disabled", period.this_year)
        rate = where(is_special_needs, special_needs_rate, standard_rate)

        # A child not actually in care draws no rate.
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        return where(in_care, rate, 0)
