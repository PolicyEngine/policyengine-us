from policyengine_us.model_api import *


class ri_rimap_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Marketplace Affordability Program applicable percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        # PDF pages 2-3: the interpolation rule (p.2) and the Plan Year 2027
        # Rhode Island Applicable Percentage Table (p.3).
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=2",
    )
    documentation = (
        "The share of household income that the Rhode Island Marketplace "
        "Affordability Program treats as affordable for the benchmark "
        "second-lowest-cost silver plan. Below 200% of the poverty line it "
        "follows the Plan Year 2027 Rhode Island Applicable Percentage "
        "Table: 0% from 100% to 150%, rising linearly from 0% to 2% between "
        "150% and 200%, in proportion to the household's position within "
        "the band. Above 400% it is a flat 18%. The table sets no "
        "percentage from 200% to 400%, so this returns 0 there; no "
        "household in that range is eligible."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.hsri.rimap
        ratio = tax_unit("ri_rimap_fpl_ratio", period)
        schedule = p.applicable_percentage
        thresholds = np.array(schedule.threshold)
        initial_rates = np.array(schedule.initial)
        final_rates = np.array(schedule.final)
        # The percentage slopes linearly within a band, which a scale
        # parameter cannot express, so the band lookup and interpolation are
        # written out, as in the New Mexico and California programs. Each
        # band includes its lower edge ("at least"), so side="right" puts a
        # ratio exactly on a threshold in the band that starts there; the
        # schedule is continuous, so the edge choice does not change the
        # percentage. Clipping keeps both band edges inside the arrays.
        band = clip(
            np.searchsorted(thresholds, ratio, side="right") - 1,
            0,
            len(initial_rates) - 1,
        )
        band_start = thresholds[band]
        band_end = thresholds[band + 1]
        position = clip((ratio - band_start) / (band_end - band_start), 0, 1)
        initial = initial_rates[band]
        final = final_rates[band]
        low_income_percentage = initial + position * (final - initial)
        return select(
            [ratio < p.fpl_limit, ratio > p.high_income.fpl_floor],
            [low_income_percentage, p.high_income.rate],
            default=0,
        )
