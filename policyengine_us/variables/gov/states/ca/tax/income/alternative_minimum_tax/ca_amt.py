from policyengine_us.model_api import *


class ca_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "California alternative minimum tax"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        amti = tax_unit("ca_amti", period)
        # Line 22
        exemption_amount = tax_unit("ca_amt_exemption", period)
        # Line 23
        reduced_amti = max_(amti - exemption_amount, 0)
        # Line 24
        p = parameters(period).gov.states.ca.tax.income.amt
        tentative_minimum_tax = reduced_amti * p.tentative_min_tax_rate
        # Line 25
        regular_tax_before_credits = tax_unit(
            "ca_income_tax_before_credits", period
        )
        # Line 26
        return max_(tentative_minimum_tax - regular_tax_before_credits, 0)
