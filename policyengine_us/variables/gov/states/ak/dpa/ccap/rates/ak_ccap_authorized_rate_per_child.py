from policyengine_us.model_api import *


class ak_ccap_authorized_rate_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP authorized reimbursement rate per child"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203"

    def formula(person, period):
        charged = person("ak_ccap_charged_rate", period)
        max_state_rate = person("ak_ccap_max_provider_rate_per_child", period)
        # When we don't track the provider's charged rate (charged = 0),
        # assume the family is charged at least the state maximum.
        return where(charged > 0, min_(charged, max_state_rate), max_state_rate)
