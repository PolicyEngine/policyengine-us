from policyengine_us.model_api import *


class mn_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota alternative minimum tax (AMT)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1mt_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1mt_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        taxinc = tax_unit("mn_amt_taxable_income", period)
        # calculate gross AMT amount
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mn.tax.income
        excess_taxinc = max_(0, taxinc - p.amt.income_threshold[filing_status])
        fractional_taxinc = excess_taxinc * p.amt.income_fraction
        fractional_threshold = p.amt.fractional_income_threshold[filing_status]
        taxinc_amount = max_(0, fractional_threshold - fractional_taxinc)
        net_taxinc = max_(0, taxinc - taxinc_amount)
        amt_gross = net_taxinc * p.amt.rate
        # calculate net AMT amount
        return max_(0, amt_gross - tax_unit("mn_basic_tax", period))
