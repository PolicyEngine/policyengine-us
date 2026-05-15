from policyengine_us.model_api import *


class ak_ccap_benefit_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP subsidy per child before copay"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203"

    def formula(person, period, parameters):
        charged = person("ak_ccap_charged_rate", period)
        max_state_rate = person("ak_ccap_max_provider_rate_per_child", period)
        sn_supplement = person("ak_ccap_special_needs_supplement", period)
        max_allowed = max_state_rate + sn_supplement
        # When we don't track the provider's charged rate (charged = 0),
        # assume the family is charged at least the state maximum so the
        # subsidy equals the state max. When charged > 0, cap at charged.
        return where(charged > 0, min_(charged, max_allowed), max_allowed)
