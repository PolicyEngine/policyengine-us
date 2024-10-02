from policyengine_us.model_api import *


class nyc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC EITC"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their NYAGI and EITC.
        ny_agi = tax_unit("ny_agi", period)
        federal_eitc = tax_unit("eitc", period)

        # Then get the EITC part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.eitc

        # Calculate the EITC before the reduction.
        percentage_pre_reduction = p.percent.calc(ny_agi)

        # Calculate the reduction (if applicable).
        threshold = p.reduction_threshold.calc(ny_agi)
        excess = max_(0, ny_agi - threshold)
        pct_point_reduction_if_applicable = p.percent_reduction * excess
        pct_point_reduction = where(
            threshold > 0, pct_point_reduction_if_applicable, 0
        )

        # Percentage is nonnegative because the last bracket is a flat 10%.
        percentage = percentage_pre_reduction - pct_point_reduction

        # Return the net EITC.
        return federal_eitc * percentage
