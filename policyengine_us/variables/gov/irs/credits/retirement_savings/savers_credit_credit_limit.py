from policyengine_us.model_api import *


class savers_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Retirement Savings Credit"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        p = parameters(period).gov.irs.credits.retirement_saving
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        return max_(income_tax_before_credits - preceding_credits, 0)
