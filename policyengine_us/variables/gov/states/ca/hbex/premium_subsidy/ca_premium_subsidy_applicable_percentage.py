from policyengine_us.model_api import *


class ca_premium_subsidy_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Premium Subsidy applicable percentage"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        # California applicable percentage of household income toward the
        # benchmark second lowest cost silver plan, bracket-interpolated
        # linearly within each federal poverty line band.
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=2",
        "https://hbex.coveredca.com/data-research/Final-2027-California-Premium-Subsidy-Program-Design.pdf#page=2",
        "https://hbex.coveredca.com/toolkit/webinars-briefings/downloads/OE27_Enroller_Kickoff.pdf#page=40",
        "https://www.ftb.ca.gov/forms/2020/2020-3849-instructions.pdf#page=6",
        "https://www.ftb.ca.gov/forms/2021/2021-3849-instructions.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=9",
    )

    def formula(tax_unit, period, parameters):
        magi_frac = tax_unit("aca_magi_fraction", period)
        magi = max_(tax_unit("aca_magi", period), 0)
        exact_magi_frac = magi / tax_unit("tax_unit_fpg", period.last_year)
        p = parameters(period).gov.states.ca.hbex.premium_subsidy.applicable_percentage

        thresholds = np.array(p.threshold)
        initial_rates = np.array(p.initial)
        final_rates = np.array(p.final)

        # The Board-adopted Designs (d)(4), operative under Gov. Code
        # 100800(c), put exactly 150% in the 0% band and income above 150%
        # in the paying band. Use the exact ratio to select the band.
        # For rounding, predecessor FTB 3849 Table 1-2 (2020/2021) tests
        # "above" on exact income before truncating for the rate lookup.
        # Form 8962 Worksheet 2 line 4 likewise checks "more than" before
        # truncation. side="left" keeps an exact threshold in the lower
        # band; clipping keeps both bracket endpoints in the rate arrays.
        # The OE27 enroller example conflicts with the adopted Designs at 150%:
        # it charges 2.80%, but (d)(4) starts the paying band "Above 150%".
        # Follow the adopted 0% boundary; the citations above document both.
        # Candidate: us-ca:premium-subsidy-150-fpl-boundary until registered.
        bracket_idx = clip(
            np.searchsorted(thresholds, exact_magi_frac, side="left") - 1,
            0,
            len(initial_rates) - 1,
        )

        bracket_start = thresholds[bracket_idx]
        bracket_end = thresholds[bracket_idx + 1]

        # Retain the truncated fraction within the band: 150.6% uses the
        # 150% lookup row of the upper band (3.19% in 2026).
        position = clip(
            (magi_frac - bracket_start) / (bracket_end - bracket_start), 0, 1
        )

        initial = initial_rates[bracket_idx]
        final = final_rates[bracket_idx]
        return initial + position * (final - initial)
