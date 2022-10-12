from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        income_is_deemed = (
            person("ssi_income_deemed_from_ineligible_spouse", period) > 0
        )
        return both_eligible | income_is_deemed
