from policyengine_us.model_api import *


class ca_exemption_amount_high_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California exemption amount for AMTI higher than threshold"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html"
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        exemption_amount_initial = p.exemption_amt[filing_status]
        amti = tax_unit("ca_amti", period)
        exemption_amount_low = p.exemption_amt_lower_threshold[filing_status]
        exemption_amount_high = max_(
            exemption_amount_initial
            - (amti - exemption_amount_low) * p.amti_rate,
            0,
        )  # line 6

        person = tax_unit.members
        eligible_child = person("ca_exemption_child_eligible", period)
        eligible_child_present = tax_unit.any(eligible_child)
        exemption_amount_child = p.exemption_amount_child
        earned_income = tax_unit("head_earned", period)
        exemption_amount_child_total = (
            exemption_amount_child * eligible_child_present + earned_income
        )  # line 9

        over_threshold = (
            tax_unit("ca_amti", period)
            >= p.exemption_amt_upper_threshold[filing_status]
        )

        return where(
            eligible_child_present,
            where(
                over_threshold,
                0,
                min_(exemption_amount_high, exemption_amount_child_total),
            ),
            where(over_threshold, 0, exemption_amount_high),
        )
