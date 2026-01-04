from policyengine_us.model_api import *


class aca_required_contribution_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA PTC phase-out rate (i.e., IRS Form 8962 'applicable figure')"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A"

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        p = parameters(period).gov.aca.required_contribution_percentage

        # Get bracket boundaries and rates
        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # Find which bracket each household falls into
        # searchsorted returns index where magi_frac would be inserted
        # subtract 1 to get the bracket index (clamped to valid range)
        # Note: there are len(thresholds)-1 brackets (rate arrays are 1 shorter than thresholds)
        bracket_idx = clip(
            np.searchsorted(thresholds, magi_frac, side="right") - 1,
            0,
            len(initial_rates) - 1,
        )

        # Get bracket boundaries for interpolation
        bracket_start = thresholds[bracket_idx]
        # For the last bracket, use a dummy end value (won't affect result since initial=final)
        # Need to use min_ to avoid index errors with vectorized operations
        next_idx = min_(bracket_idx + 1, len(thresholds) - 1)
        bracket_end = where(
            bracket_idx < len(thresholds) - 1,
            thresholds[next_idx],
            bracket_start + 1,  # Dummy value for last bracket
        )

        # Calculate position within bracket (0 to 1)
        bracket_width = bracket_end - bracket_start
        position = where(
            bracket_width > 0,
            (magi_frac - bracket_start) / bracket_width,
            0,
        )
        position = clip(position, 0, 1)

        # Interpolate between initial and final rates
        initial = initial_rates[bracket_idx]
        final = final_rates[bracket_idx]
        return initial + position * (final - initial)
