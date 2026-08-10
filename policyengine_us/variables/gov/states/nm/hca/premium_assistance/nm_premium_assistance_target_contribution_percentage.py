from policyengine_us.model_api import *


class nm_premium_assistance_target_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Premium Assistance target contribution percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.NM
    # New Mexico target contribution percentage toward the benchmark SLCSP for
    # base premium assistance, bracket-interpolated across FPL bands.
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=4",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(
            period
        ).gov.states.nm.hca.premium_assistance.target_contribution_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # NOTE: the target percentage slopes linearly WITHIN each FPL band, which
        # a core scale parameter cannot express (scales return a flat value per
        # bracket), so we hand-roll the bracket lookup and interpolation.
        #
        # searchsorted returns the insertion index; subtract 1 for the bracket
        # index, clipped so bracket_idx + 1 is always a valid threshold index.
        bracket_idx = clip(
            np.searchsorted(thresholds, magi_frac, side="right") - 1,
            0,
            len(initial_rates) - 1,
        )

        # Canonical within-band interpolation: clip guarantees bracket_idx + 1
        # is in range and each band has positive width, so no fallback is needed.
        bracket_start = thresholds[bracket_idx]
        bracket_end = thresholds[bracket_idx + 1]
        position = clip(
            (magi_frac - bracket_start) / (bracket_end - bracket_start),
            0,
            1,
        )

        initial = initial_rates[bracket_idx]
        final = final_rates[bracket_idx]
        return initial + position * (final - initial)
