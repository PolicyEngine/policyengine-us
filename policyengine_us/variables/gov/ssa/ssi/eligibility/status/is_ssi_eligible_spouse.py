from policyengine_us.model_api import *


class is_ssi_eligible_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-eligible spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#b"

    def formula(person, period, parameters):
        # Both members of a joint claim are eligible spouses. The member in
        # the tax-unit spouse role carries this label and the other remains
        # the eligible individual, so each couple keeps one of each.
        spouse = person("is_tax_unit_spouse", period)
        return spouse & person("ssi_claim_is_joint", period)
