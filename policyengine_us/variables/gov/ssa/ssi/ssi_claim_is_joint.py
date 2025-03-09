from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR

    def formula(person, period, parameters):
        both_eligible = person("ssi_marital_both_eligible", period)
        deemed_income = person("ssi_income_deemed_from_ineligible_spouse", period) > 0
        return both_eligible | deemed_income
