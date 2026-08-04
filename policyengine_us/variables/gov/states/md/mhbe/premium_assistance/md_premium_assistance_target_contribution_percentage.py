from policyengine_us.model_api import *


class md_premium_assistance_target_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Premium Assistance target contribution percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/pubs/committee/AELR/25-134E-Regulation.pdf#page=5",
        "https://mgaleg.maryland.gov/meeting_material/2025/hgo%20-%20134051066649659653%20-%20Combined%20MHBE.MIA%20slides_10.16.2025%20briefing%20to%20HGO&Finance.pdf#page=58",
    )
    documentation = (
        "Maryland target contribution percentage toward the benchmark SLCSP, "
        "bracket-interpolated across FPL bands, then reduced by the Young "
        "Adult Subsidy overlay and floored at zero."
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(
            period
        ).gov.states.md.mhbe.premium_assistance.target_contribution_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # Find which bracket each tax unit falls into. searchsorted returns
        # the index where magi_frac would be inserted; subtract 1 to get the
        # bracket index, clamped to the valid range.
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
        base_percentage = initial + position * (final - initial)

        # Subtract the Young Adult Subsidy reduction, floored at zero.
        young_adult_reduction = tax_unit(
            "md_premium_assistance_young_adult_reduction", period
        )
        return max_(0, base_percentage - young_adult_reduction)
