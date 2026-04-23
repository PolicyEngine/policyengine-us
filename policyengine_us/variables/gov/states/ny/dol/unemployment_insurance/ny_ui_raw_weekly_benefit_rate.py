from policyengine_us.model_api import *


class ny_ui_raw_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "NY UI raw weekly benefit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        high_quarter_wages = person("ny_ui_high_quarter_wages", period)
        second_high_quarter_wages = person("ny_ui_second_high_quarter_wages", period)
        quarters_with_wages = person("ny_ui_quarters_with_wages", period)

        four_quarter_case = quarters_with_wages >= 4

        # Four-quarter formula: high quarter wages divided by the standard
        # divisor (or the low divisor when wages are at or below the low
        # threshold).
        divisor_four_quarter = where(
            high_quarter_wages > p.low_hq_threshold,
            p.standard_divisor,
            p.low_divisor,
        )
        raw_four_quarter = np.floor(high_quarter_wages / divisor_four_quarter)

        # Two- or three-quarter formula has three tiers:
        #   Tier 1: high quarter wages above two-quarter threshold ($4,000) →
        #       average of two highest quarters divided by standard divisor.
        #   Tier 2: high quarter wages above low threshold ($3,575) but at or
        #       below two-quarter threshold → high quarter wages / standard
        #       divisor.
        #   Tier 3: high quarter wages at or below low threshold → high
        #       quarter wages / low divisor.
        average_two_quarters = (high_quarter_wages + second_high_quarter_wages) / 2
        raw_two_three_tier_1 = np.floor(average_two_quarters / p.standard_divisor)
        raw_two_three_tier_2 = np.floor(high_quarter_wages / p.standard_divisor)
        raw_two_three_tier_3 = np.floor(high_quarter_wages / p.low_divisor)

        raw_two_three_quarter = select(
            [
                high_quarter_wages > p.two_quarter_hq_threshold,
                high_quarter_wages > p.low_hq_threshold,
            ],
            [raw_two_three_tier_1, raw_two_three_tier_2],
            default=raw_two_three_tier_3,
        )

        return where(four_quarter_case, raw_four_quarter, raw_two_three_quarter)
