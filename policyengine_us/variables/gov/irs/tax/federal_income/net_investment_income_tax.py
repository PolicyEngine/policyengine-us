from policyengine_us.model_api import *


class net_investment_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net Investment Income Tax"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=11",
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.investment.net_investment_income_tax
        threshold = p.threshold[tax_unit("filing_status", period)]
        magi = tax_unit("niit_magi", period)
        excess_magi = max_(0, magi - threshold)
        base = min_(
            max_(0, tax_unit("net_investment_income", period)),
            excess_magi,
        )
        return p.rate * base
