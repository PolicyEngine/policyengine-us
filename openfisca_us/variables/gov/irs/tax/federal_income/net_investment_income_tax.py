from openfisca_us.model_api import *


class net_investment_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net Investment Income Tax"
    reference = "https://www.law.cornell.edu/uscode/text/26/1411"
    unit = USD

    def formula(tax_unit, period, parameters):
        NII_ELEMENTS = [
            "taxable_interest_income",
            "non_qualified_dividend_income",
            "c01000",
            "rental_income",
        ]
        nii = max_(0, add(tax_unit, period, NII_ELEMENTS))
        p = parameters(period).gov.irs.investment.net_investment_income_tax
        threshold = p.threshold[tax_unit("filing_status", period)]
        base = min_(
            nii, max_(0, tax_unit("adjusted_gross_income", period) - threshold)
        )
        return p.rate * base
