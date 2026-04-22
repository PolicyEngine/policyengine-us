from datetime import date

from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.me.dhhs.ccap.payment.me_ccap_provider_type import (
    MECCAPProviderType,
)
from policyengine_us.variables.gov.states.me.dhhs.ccap.payment.me_ccap_region import (
    MECCAPRegion,
)


class me_ccap_market_rate(Variable):
    value_type = float
    entity = Person
    label = "Maine CCAP weekly market rate per child"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ccap_eligible_child"
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=25"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ccap.market_rate
        region = person.household("me_ccap_region", period)
        age_group = person("me_ccap_age_group", period)
        time_category = person("me_ccap_time_category", period)
        provider_type = person("me_ccap_provider_type", period)

        def rate_for(provider_rates):
            if period.start.date < date(2024, 7, 6):
                return select(
                    [
                        region == MECCAPRegion.ANDROSCOGGIN,
                        region == MECCAPRegion.AROOSTOOK,
                        region == MECCAPRegion.CUMBERLAND,
                        region == MECCAPRegion.FRANKLIN,
                        region == MECCAPRegion.HANCOCK,
                        region == MECCAPRegion.KENNEBEC,
                        region == MECCAPRegion.KNOX,
                        region == MECCAPRegion.LINCOLN,
                        region == MECCAPRegion.OXFORD,
                        region == MECCAPRegion.PENOBSCOT,
                        region == MECCAPRegion.PISCATAQUIS,
                        region == MECCAPRegion.SAGADAHOC,
                        region == MECCAPRegion.SOMERSET,
                        region == MECCAPRegion.WALDO,
                        region == MECCAPRegion.WASHINGTON,
                        region == MECCAPRegion.YORK,
                    ],
                    [
                        provider_rates.ANDROSCOGGIN[age_group][time_category],
                        provider_rates.AROOSTOOK[age_group][time_category],
                        provider_rates.CUMBERLAND[age_group][time_category],
                        provider_rates.FRANKLIN[age_group][time_category],
                        provider_rates.HANCOCK[age_group][time_category],
                        provider_rates.KENNEBEC[age_group][time_category],
                        provider_rates.KNOX[age_group][time_category],
                        provider_rates.LINCOLN[age_group][time_category],
                        provider_rates.OXFORD[age_group][time_category],
                        provider_rates.PENOBSCOT[age_group][time_category],
                        provider_rates.PISCATAQUIS[age_group][time_category],
                        provider_rates.SAGADAHOC[age_group][time_category],
                        provider_rates.SOMERSET[age_group][time_category],
                        provider_rates.WALDO[age_group][time_category],
                        provider_rates.WASHINGTON[age_group][time_category],
                        provider_rates.YORK[age_group][time_category],
                    ],
                    default=provider_rates.AROOSTOOK[age_group][time_category],
                )

            return provider_rates[region][age_group][time_category]

        center_rate = rate_for(p.licensed_center)
        family_rate = rate_for(p.licensed_family)
        exempt_rate = rate_for(p.license_exempt)

        return select(
            [
                provider_type == MECCAPProviderType.LICENSED_CENTER,
                provider_type == MECCAPProviderType.LICENSED_FAMILY,
                provider_type == MECCAPProviderType.LICENSE_EXEMPT,
            ],
            [
                center_rate,
                family_rate,
                exempt_rate,
            ],
            default=center_rate,
        )
