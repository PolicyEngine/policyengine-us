from policyengine_us.model_api import *


class ca_amt_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMT exemption amount"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html"
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        exemption_amount_initial = p.exemption.amount[filing_status]
        amti = tax_unit("ca_amti", period)
        exemption_amount_low = p.exemption.amt_threshold.lower[filing_status]
        exemption_amount_high = max_(
            exemption_amount_initial
            - (amti - exemption_amount_low) * p.amti.rate,
            0,
        )  # Instructions for Schedule P 540, line 22, Exemption Worksheet, line 6

        person = tax_unit.members
        eligible_child = person("ca_child_exemption_eligible", period)
        eligible_child_present = tax_unit.any(eligible_child)
        exemption_amount_child = p.exemption.amount_child
        earned_income = tax_unit("head_earned", period)
        exemption_amount_child_total = (
            exemption_amount_child * eligible_child_present + earned_income
        )  # Instructions for Schedule P 540, line 22, Exemption Worksheet, line 9

        over_threshold = (
            tax_unit("ca_amti", period)
            >= p.exemption.amt_threshold.upper[filing_status]
        )

        exemption_amt_eligible_child = where(
            over_threshold,
            0,
            min_(exemption_amount_high, exemption_amount_child_total),
        )

        exemption_amt_no_eligible_child = where(
            over_threshold, 0, exemption_amount_high
        )

        return where(
            eligible_child_present,
            exemption_amt_eligible_child,
            exemption_amt_no_eligible_child,
        )
