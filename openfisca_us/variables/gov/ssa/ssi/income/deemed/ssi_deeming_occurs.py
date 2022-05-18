from openfisca_us.model_api import *


class ssi_deeming_occurs(Variable):
    value_type = bool
    entity = MaritalUnit
    label = "SSI deeming occurs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163#d"

    def formula(marital_unit, period, parameters):
        ineligible_spouse_income = (
            marital_unit("ssi_ineligible_spouse_countable_income", period)
            / MONTHS_IN_YEAR
        )
        amounts = parameters(period).ssa.ssi.amounts
        return ineligible_spouse_income > (amounts.couple - amounts.individual)
