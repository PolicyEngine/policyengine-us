from policyengine_us.model_api import *


class is_ssi_eligible_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-eligible spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#b"

    def formula(person, period, parameters):
        # This label follows the tax-unit spouse role within a joint claim.
        # A married couple with no tax-unit spouse role has no member
        # carrying the eligible-spouse label.
        spouse = person("is_tax_unit_spouse", period)
        return spouse & person("ssi_claim_is_joint", period)
