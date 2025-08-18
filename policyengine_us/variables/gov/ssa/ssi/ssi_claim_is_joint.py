from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR

    def formula(person, period, parameters):
        abd_person = person("is_ssi_aged_blind_disabled", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_person = abd_person & is_head_or_spouse

        return person.marital_unit.sum(eligible_person) > 1
