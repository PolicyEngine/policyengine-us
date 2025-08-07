from policyengine_us.model_api import *
from numpy import ceil


class me_dependent_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine dependent exemption credit"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-SS.html"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):

        # Get their Maine AGI (line 3).
        me_agi = tax_unit("me_agi", period)

        # Then get the Maine Dependents Exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.dependent_exemption

        # Calculate the maximum dependents exemption amount (line 2).
        max_amount = add(
            tax_unit, period, ["me_dependent_exemption_credit_amount_person"]
        )

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the phaseout start amount based on filing status (line 4).
        phaseout_start = p.phase_out.start[filing_status]

        # Get the excess amount, if any, in thousands of dollars (rounded up) [lines 5 and 6].
        excess = max_(me_agi - phaseout_start, 0)
        increments = ceil(excess / p.phase_out.increment)

        # Calculate the excess part phase out amount (line 7).
        phase_out_amount = increments * p.phase_out.step

        # Return the max exemption amount minus the phaseout amount (line 8).
        return max_(max_amount - phase_out_amount, 0)
