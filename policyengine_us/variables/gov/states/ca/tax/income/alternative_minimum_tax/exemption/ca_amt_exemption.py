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
        p = parameters(
            period
        ).gov.states.ca.tax.income.alternative_minimum_tax.exemption
        filing_status = tax_unit("filing_status", period)
        exemption_eligiblity_threshold = p.amti.threshold.upper[filing_status]
        amti = tax_unit("ca_amti", period)
        exemption_eligible = amti < exemption_eligiblity_threshold
        # Instructions for Schedule P 540, line 22, Exemption Worksheet,
        # Line 1
        exemption_mac_amount = p.amount[filing_status]
        # Line 2 - AMTI
        # Line 3
        lower_exemption_threshold = p.amti.threshold.lower[filing_status]
        # Line 4
        reduced_amti = max_(amti - lower_exemption_threshold, 0)
        # Line 5
        reduced_amti_rate = reduced_amti * p.amti.rate
        # Line 6
        adult_exemption = max_(exemption_mac_amount - reduced_amti_rate, 0)
        # Eligible children receive an increased exemption amount
        person = tax_unit.members
        eligible_child = person("ca_child_exemption_eligible", period)
        head_is_eligible_child = tax_unit.any(eligible_child)
        # Line 7
        exemption_amount_child = p.amount_child
        # Line 8
        earned_income = tax_unit("head_earned", period)
        # Line 9
        total_reduced_exemption_amount = exemption_amount_child + earned_income
        # Line 10
        child_exemption = min_(total_reduced_exemption_amount, adult_exemption)
        total_exemption = where(
            head_is_eligible_child, child_exemption, adult_exemption
        )
        return where(exemption_eligible, total_exemption, 0)
