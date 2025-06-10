from policyengine_us.model_api import *


class cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        expenses = tax_unit("cdcc_relevant_expenses", period)
        rate = tax_unit("cdcc_rate", period)
        return expenses * rate
