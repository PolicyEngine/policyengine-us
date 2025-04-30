from policyengine_us.model_api import *


class amt_lower_base_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax lower base tax amount"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others' - lower bracket"
    reference = "https://www.irs.gov/pub/irs-pdf/f6251.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.income.amt
        filing_status = tax_unit("filing_status", period)
        reduced_income = tax_unit("amt_income_less_exemptions", period)
        bracket_fraction = p.multiplier[filing_status]
        tax_rate_threshold = p.brackets.thresholds[-1] * bracket_fraction
        lower_rate = p.brackets.rates[0]
        return min_(reduced_income, tax_rate_threshold) * lower_rate
