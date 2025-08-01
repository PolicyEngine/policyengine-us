from policyengine_us.model_api import *


class lifetime_learning_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lifetime Learning Credit credit limit"
    unit = USD
    documentation = "Value of the non-refundable Lifetime Learning Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        p = parameters(
            period
        ).gov.irs.credits.education.lifetime_learning_credit
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        return max_(income_tax_before_credits - preceding_credits, 0)
