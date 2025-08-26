from policyengine_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    label = "SSI amount if eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#b"

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.amount
        is_dependent = person("is_tax_unit_dependent", period)
        head_or_spouse_amount = where(
            person("ssi_claim_is_joint", period),
            p.couple / 2,
            p.individual,
        )
        # Adults amount is based on whether it is a joint claim
        # Dependents always use individual amount.
        ssi_per_month = where(
            is_dependent, p.individual, head_or_spouse_amount
        )
        return ssi_per_month * MONTHS_IN_YEAR
