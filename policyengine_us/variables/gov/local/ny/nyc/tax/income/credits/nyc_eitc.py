from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ny.tax.income.adjusted_gross_income.ny_recomputed_federal_agi import (
    get_ny_recomputed_branch,
)


class nyc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC EITC"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/1310",
        "https://www.tax.ny.gov/pdf/2025/inc/it215i_2025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        # First get their NYAGI and EITC.
        ny_agi = tax_unit("ny_agi", period)
        # The federal credit recomputed with recomputed federal AGI (IT-201
        # line 19a; IT-215 instructions) when it differs from federal AGI.
        branch = get_ny_recomputed_branch(tax_unit, period)
        if branch is None:
            federal_eitc = tax_unit("eitc", period)
        else:
            federal_eitc = branch.calculate("eitc", period)

        # Then get the EITC part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.eitc

        # Calculate the EITC before the reduction.
        percentage_pre_reduction = p.percent.calc(ny_agi)

        # Calculate the reduction (if applicable).
        threshold = p.reduction_threshold.calc(ny_agi)
        excess = max_(0, ny_agi - threshold)
        pct_point_reduction_if_applicable = p.percent_reduction * excess
        pct_point_reduction = where(threshold > 0, pct_point_reduction_if_applicable, 0)

        # From 2022, worksheet line 4 rounds the reduction with halves up.
        # Protect exact halves from floating-point error before taking the floor.
        pct_point_reduction = where(
            period.start.year >= 2022,
            np.floor(np.nextafter(pct_point_reduction * 10_000, np.inf) + 0.5) / 10_000,
            pct_point_reduction,
        )

        # Percentage is nonnegative because the last bracket is a flat 10%.
        percentage = percentage_pre_reduction - pct_point_reduction

        # Return the net EITC.
        return federal_eitc * percentage
