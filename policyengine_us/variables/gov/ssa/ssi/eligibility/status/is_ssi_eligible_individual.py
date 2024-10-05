from policyengine_us.model_api import *


class is_ssi_eligible_individual(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-eligible individual"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#a"

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        is_ssi_eligible_spouse = person("is_ssi_eligible_spouse", period)
        return aged_blind_disabled & ~is_ssi_eligible_spouse
