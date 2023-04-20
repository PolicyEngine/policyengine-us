from policyengine_us.model_api import *


class me_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Line 1. First get their Maine AGI.
        me_agi = tax_unit("me_agi", period)

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get overall deduction part of parameters tree
        p = parameters(period).gov.states.me.tax.income.deductions.phase_out

        # Calculate the deduction phase-out parameters based on
        # filing status.
        phaseout_start = p.start[filing_status]
        excess = max_(me_agi - phaseout_start, 0)  # Line 3
        phaseout_width = p.width[filing_status]  # Line 4
        phaseout_percent = min_(1, excess / phaseout_width)  # Line 5

        # Get their deduction prior to phaseout. Max of itemized and standard (Line 6)
        max_deduction = max_(
            tax_unit("me_itemized_deductions", period),
            tax_unit("me_standard_deduction", period),
        )

        # Calculate the phaseout amount (Line 7)
        phaseout_amount = max_deduction * phaseout_percent

        return max_deduction - phaseout_amount  # Line 8
