from policyengine_us.model_api import *


class is_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Is veteran"
    documentation = "A person who served in the active military, naval, air, or space service, and who was discharged or released therefrom under conditions other than dishonorable."
    reference = "https://www.law.cornell.edu/uscode/text/38/101"  # (2)
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("veterans_benefits", period) > 0
