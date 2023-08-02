from policyengine_us.model_api import *


class me_personal_exemption_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine personal exemption deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # First get their Maine AGI.
        me_agi = tax_unit("me_agi", period)

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the Maine Personal Credit part of the parameter tree.
        p = parameters(
            period
        ).gov.states.me.tax.income.deductions.personal_exemption

        # Calculate the Personal Exemption phase-out parameters based on
        # filing status.
        phaseout_start = p.phaseout.start[filing_status]
        excess = max_(me_agi - phaseout_start, 0)  # Line 3
        phaseout_width = p.phaseout.width[filing_status]  # Line 4
        phaseout_percent = min_(1, excess / phaseout_width)  # Line 5

        # Get their Maine personal exemptions (line 6).
        exemptions = tax_unit(
            "num", period
        )  # Number of people in the tax unit.
        max_amount = exemptions * p.amount

        # Calculate the phaseout amount (line 7).
        phaseout_amount = phaseout_percent * max_amount

        return max_amount - phaseout_amount  # Line 8
