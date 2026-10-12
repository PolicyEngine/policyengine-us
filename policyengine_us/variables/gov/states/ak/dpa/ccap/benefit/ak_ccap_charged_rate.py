from policyengine_us.model_api import *


class ak_ccap_charged_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP provider-charged rate per child (input)"
    documentation = "This is an input variable representing the actual rate the provider charges per child. PolicyEngine households default to 0 unless explicitly set."
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=598"
