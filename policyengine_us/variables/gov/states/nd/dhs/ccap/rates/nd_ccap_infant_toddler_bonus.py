from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_provider_type import (
    NDCCAPProviderType,
)


class nd_ccap_infant_toddler_bonus(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "North Dakota CCAP infant/toddler bonus per child"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible_child"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.rates
        # The infant/toddler bonus is a flat per-child provider payment for
        # children attending 40 or more hours per month, paid to North Dakota
        # licensed, tribally licensed, or military licensed providers
        # (400-28-100-30). The bonus is additive: it is not capped at the
        # family's billed expenses and not reduced by the co-payment. The
        # parameter is zero for preschool and school-age children, so the age
        # filter is handled by the lookup.
        age_group = person("nd_ccap_age_group", period)
        bonus_amount = p.infant_toddler_bonus[age_group]
        # PolicyEngine tracks weekly child care hours, so the 40-hours-per-month
        # attendance condition is approximated against a weekly threshold.
        hours = person("childcare_hours_per_week", period.this_year)
        meets_hours = hours >= p.infant_toddler_bonus_min_weekly_hours
        # We do not track the provider's licensure jurisdiction, so we assume
        # the licensure condition is met for all providers other than approved
        # relatives.
        provider_type = person("nd_ccap_provider_type", period)
        eligible_provider = provider_type != NDCCAPProviderType.APPROVED_RELATIVE
        return bonus_amount * meets_hours * eligible_provider
