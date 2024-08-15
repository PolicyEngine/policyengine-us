from policyengine_us.model_api import *


class ca_cspp(Variable):
    value_type = float
    entity = Person
    label = "Amount of California State Preschool Program benefit"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return person("head_start", period)
