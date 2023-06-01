from policyengine_us.model_api import *


class me_deduction_phaseout_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine deduction phaseout percentage"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf",
    )
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

        # Calculate the phaseout percent (Line 5)
        return min_(1, excess / phaseout_width)
