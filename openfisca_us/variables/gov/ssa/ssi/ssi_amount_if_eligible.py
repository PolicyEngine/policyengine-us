from openfisca_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    label = "SSI amount if eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382#b"

    def formula(person, period, parameters):
        has_eligible_spouse = spouse(person, period, "is_ssi_eligible_spouse")
        has_income_deemed_from_ineligible_spouse = person("ssi_income_deemed_from_ineligible_spouse", period) > 0
        ssi = parameters(period).ssa.ssi.amount
        return where(
            has_eligible_spouse & has_income_deemed_from_ineligible_spouse,
            ssi.couple,
            ssi.individual,
        )
