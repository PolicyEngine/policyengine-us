from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_time_category import (
    NDCCAPTimeCategory,
)


class nd_ccap_qris_step_bonus(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "North Dakota CCAP QRIS step bonus per child"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible_child"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.rates
        # The QRIS step bonus is a separate provider payment computed as a
        # share of the base state maximum rate by quality step (400-28-100-30).
        # It uses the base rate excluding the special-needs +10% to avoid
        # compounding the two provisions. The bonus is additive: it is not
        # capped at the family's billed expenses and not reduced by the
        # co-payment.
        provider_type = person("nd_ccap_provider_type", period)
        age_group = person("nd_ccap_age_group", period)
        time_category = person("nd_ccap_time_category", period)
        base_rate = where(
            time_category == NDCCAPTimeCategory.FULL_TIME,
            p.full_time[provider_type][age_group],
            p.part_time[provider_type][age_group],
        )
        qris_step = person("nd_ccap_provider_qris_step", period)
        bonus_rate = p.qris_step_bonus_rate[qris_step]
        return base_rate * bonus_rate
