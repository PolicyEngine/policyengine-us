from policyengine_us.model_api import *


class ak_ccap_benefit_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP subsidy per child before copay"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203"

    def formula(person, period):
        authorized = person("ak_ccap_authorized_rate_per_child", period)
        sn_supplement = person("ak_ccap_special_needs_supplement", period)
        return authorized + sn_supplement
