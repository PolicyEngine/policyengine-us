from policyengine_us.model_api import *


class nm_premium_assistance_target_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Premium Assistance target contribution percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=4",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=5",
    )
    documentation = (
        "New Mexico target contribution percentage toward the benchmark SLCSP "
        "for base premium assistance, bracket-interpolated across FPL bands."
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(
            period
        ).gov.states.nm.hca.premium_assistance.target_contribution_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # The New Mexico target percentage interpolates linearly *within* each
        # FPL band (from the band's initial rate to its final rate), which a
        # core single_amount/rate scale parameter cannot express - scales return
        # a flat value per bracket. We therefore hand-roll the bracket lookup
        # and within-band interpolation with searchsorted. Do not "simplify"
        # this into a scale parameter; it would drop the within-band slope.
        #
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
        # bracket_idx is clipped to len(initial_rates) - 1, one short of the
        # final threshold index, so the where always takes the true branch for
        # any in-range value; the bracket_start + 1 fallback is a defensive
        # guard against a zero-width final bracket and is not reached with the
        # current parameter table.
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
