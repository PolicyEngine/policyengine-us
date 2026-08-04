from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.dcbs.ccap.ky_ccap_provider_type import (
    KYCCAPProviderType,
)


class ky_ccap_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Kentucky CCAP daily maximum payment rate"
    definition_period = MONTH
    defined_for = "ky_ccap_eligible_child"
    reference = "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc300kymaxpaymentchart.pdf#page=1"

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 10(1): the maximum payment is the daily rate from
        # DCC-300, keyed by county (rate region) x provider type x age group x
        # day length.
        p = parameters(period).gov.states.ky.dcbs.ccap.rates
        region = person.household("ky_ccap_rate_region", period)
        age_category = person("ky_ccap_child_age_category", period)
        day_length = person("ky_ccap_day_length", period)
        provider_type = person("ky_ccap_provider_type", period)

        types = KYCCAPProviderType
        return select(
            [
                provider_type == types.LICENSED_TYPE_I,
                provider_type == types.LICENSED_TYPE_II,
                provider_type == types.CERTIFIED,
                provider_type == types.REGISTERED,
            ],
            [
                p.licensed_type_i[region][age_category][day_length],
                p.licensed_type_ii[region][age_category][day_length],
                p.certified[region][age_category][day_length],
                p.registered[region][age_category][day_length],
            ],
        )
