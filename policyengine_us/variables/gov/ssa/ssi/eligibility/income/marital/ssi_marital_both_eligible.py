from policyengine_us.model_api import *


class ssi_marital_both_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Both members of the marital unit are eligible for SSI"
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)

        return person.marital_unit.sum(eligible) == 2
