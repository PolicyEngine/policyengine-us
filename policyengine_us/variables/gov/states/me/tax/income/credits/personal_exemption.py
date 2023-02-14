from policyengine_us.model_api import *


class personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine Personal Exemption Credit"
    unit = USD
    definition_period = YEAR
    # defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their Maine AGI.
        me_agi = tax_unit("me_agi", period)

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the Maine Personal Credit part of the parameter tree.
        p = parameters(period).gov.states.me.tax.income.credits.personal_exemption

        # Calculate the EITC before the reduction.
        percentage_pre_reduction = p.percent.calc(ny_agi)

        # Calculate the reduction (if applicable).
        threshold = p.reduction_threshold.calc(ny_agi)
        excess = max_(0, ny_agi - threshold)
        pct_point_reduction_if_applicable = p.percent_reduction * excess
        pct_point_reduction = where(threshold > 0, pct_point_reduction_if_applicable, 0)

        # Percentage is nonnegative because the last bracket is a flat 10%.
        percentage = percentage_pre_reduction - pct_point_reduction

        # Return the net EITC.
        return federal_eitc * percentage
