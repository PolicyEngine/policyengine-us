from policyengine_us.model_api import *


class amt_base_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others'"
    reference = "https://www.irs.gov/pub/irs-pdf/f6251.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.income.amt
        filing_status = tax_unit("filing_status", period)
        reduced_income = tax_unit("amt_income_less_exemptions", period)
        bracket_fraction = where(
            filing_status == filing_status.possible_values.SEPARATE,
            0.5,
            1.0,
        )
        tax_rate_threshold = p.brackets.thresholds[-1] * bracket_fraction
        lower_rate = p.brackets.rates[0]
        higher_rate = p.brackets.rates[1]
        lower_tax = min_(reduced_income, tax_rate_threshold) * lower_rate
        higher_tax = max_(0, reduced_income - tax_rate_threshold) * higher_rate
        return lower_tax + higher_tax
