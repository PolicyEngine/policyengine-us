from openfisca_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    label = "SSI amount if eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#b"

    def formula(person, period, parameters):
        ssi = parameters(period).gov.ssa.ssi.amount
        return (
            where(
                person("ssi_claim_is_joint", period),
                ssi.couple,
                ssi.individual,
            )
            * MONTHS_IN_YEAR
        )
