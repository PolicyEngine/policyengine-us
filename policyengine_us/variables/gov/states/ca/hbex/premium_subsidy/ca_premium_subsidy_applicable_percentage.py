from policyengine_us.model_api import *


class ca_premium_subsidy_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Premium Subsidy applicable percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=2",
        "https://hbex.coveredca.com/stakeholders/PDFs/2026-02_StatePremiumSub_PolicyExplainer-Final.pdf#page=2",
    )
    documentation = (
        "California applicable percentage of household income toward the "
        "benchmark second lowest cost silver plan, bracket-interpolated in a "
        "linear manner within each federal poverty line band."
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(period).gov.states.ca.hbex.premium_subsidy.applicable_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # Find which bracket each tax unit falls into. searchsorted returns
        # the index where magi_frac would be inserted; subtract 1 to get the
        # bracket index, clamped to the valid range. Rate arrays are one
        # shorter than thresholds (federal/NM convention).
        bracket_idx = clip(
            np.searchsorted(thresholds, magi_frac, side="right") - 1,
            0,
            len(initial_rates) - 1,
        )

        bracket_start = thresholds[bracket_idx]
        next_idx = min_(bracket_idx + 1, len(thresholds) - 1)
        bracket_end = where(
            bracket_idx < len(thresholds) - 1,
            thresholds[next_idx],
            bracket_start + 1,
        )

        bracket_width = bracket_end - bracket_start
        position = where(
            bracket_width > 0,
            (magi_frac - bracket_start) / bracket_width,
            0,
        )
        position = clip(position, 0, 1)

        initial = initial_rates[bracket_idx]
        final = final_rates[bracket_idx]
        return initial + position * (final - initial)
