from policyengine_us.model_api import *


class la_ccap_daily_rate(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Louisiana CCAP state maximum daily rate"
    unit = USD
    reference = "https://www.doa.la.gov/media/ny1gpl0g/2205.pdf#page=8"
    defined_for = "la_ccap_eligible_child"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.rates
        provider_type = person("la_ccap_provider_type", period.this_year)
        age_group = person("la_ccap_age_group", period.this_year)
        # LAC 28:CLXV.515.A: the Special Needs Care Incentive rate applies to
        # children qualifying for care for children with disabilities (§103).
        special_needs = person("la_ccap_special_needs_child", period)
        regular_rate = p.regular[provider_type][age_group]
        special_needs_rate = p.special_needs[provider_type][age_group]
        return where(special_needs, special_needs_rate, regular_rate)
