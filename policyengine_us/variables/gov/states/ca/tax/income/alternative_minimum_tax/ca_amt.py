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
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        exemption_amount = where(
            tax_unit("ca_amti_calc", period)
            <= p.exemption.amt_threshold.lower[filing_status],
            p.exemption.amount[filing_status],
            tax_unit("ca_exemption_amount_high_amti", period),
        )  # complete the Exemption Worksheet to figure the amount to enter on line 22.
        amti_sub_eamt = max_(
            tax_unit("ca_amti_calc", period) - exemption_amount, 0
        )  # Subtract line 22 from line 21.
        tentative_minimum_tax = amti_sub_eamt * p.tentative_min_tax_rate
        regular_tax_before_credits = tax_unit(
            "ca_income_tax_before_credits", period
        )  # line 25 from Form 540, line 31
        return max_(tentative_minimum_tax - regular_tax_before_credits, 0)
