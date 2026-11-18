from policyengine_us.model_api import *


class ca_amt_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMT exemption amount"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html",
        "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.amt.exemption
        filing_status = tax_unit("filing_status", period)
        amti = tax_unit("ca_amti", period)
        # Instructions for Schedule P 540, line 22, Exemption Worksheet,
        # Line 1
        exemption_max_amount = p.amount[filing_status]
        # Line 2 - AMTI
        # Line 3
        lower_exemption_threshold = p.amti.threshold.lower[filing_status]
        # Line 4
        reduced_amti = max_(amti - lower_exemption_threshold, 0)
        # Line 5
        reduced_amti_rate = reduced_amti * p.phase_out_rate
        # Line 6
        adult_exemption = max_(exemption_max_amount - reduced_amti_rate, 0)
        # Eligible children receive an increased exemption amount.
        # This applies when the HEAD of the tax unit is a child dependent.
        person = tax_unit.members
        eligible_child = person("is_qualifying_child_dependent", period)
        is_head = person("is_tax_unit_head", period)
        head_is_eligible_child = tax_unit.any(eligible_child & is_head)
        # Line 7: California's own amount, not the federal IRC 59(j) one.
        exemption_amount_child = p.child.amount
        # Line 8: "wages, tips, and other payments received for personal
        # services performed", which in California include payroll HSA
        # contributions. Strike benefits, which ca_head_earned counts for the
        # dependent care credit (FTB 3506 line 4), are not payments for
        # personal services, so they come out here (floored at zero, which
        # gives the same result as leaving them out before the floor).
        strike_benefits = tax_unit.sum(
            person("taxable_strike_benefits", period) * is_head
        )
        earned_income = max_(tax_unit("ca_head_earned", period) - strike_benefits, 0)
        # Line 9
        total_reduced_exemption_amount = exemption_amount_child + earned_income
        # Line 10
        child_exemption = min_(total_reduced_exemption_amount, adult_exemption)
        return where(head_is_eligible_child, child_exemption, adult_exemption)
