from policyengine_us.model_api import *


class cdcc_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child/dependent care credit credit limit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        p = parameters(period).gov.irs.credits.cdcc
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        return max_(income_tax_before_credits - preceding_credits, 0)
