from openfisca_us.model_api import *


class ny_cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # Under the law (s. 606(1)), the NY CDCC defined at its core as:
        # (federal CDCC) x (some percentage)
        # There is also another important part: s. (1-b), which amends this to:
        # (federal CDCC) x (some percentage) x (some other percentage based on NY AGI)
        # The last complication is that in (1) people with income under $40,000 are
        # treated differently than people with income over $40,000.

        # First, we'll calculate the first percentage. We calculate the percentage
        # for people under $40k, and then the percentage if over $40k, and then use the
        # correct one with a final check.

        # The core logic for both income groups is the same:
        # percentage = "A%" + (greater of: $B or ($C - NY AGI)) / $D
        # where A, B, C and D are parameters set by law. The law doesn't give
        # any intuitive names for these parameters.

        ny_agi = tax_unit("ny_agi", period)
        percentage = parameters(
            period
        ).gov.states.ny.tax.income.credits.cdcc.percentage
        main = percentage.main
        main_numerator = main.fraction.numerator
        fraction = (
            max_(0, min_(main_numerator.min, main_numerator.top - ny_agi))
            / main.fraction.denominator
        )
        main_percentage = main.base_percentage + fraction * main.multiplier

        alternate = percentage.alternate
        alternate_numerator = alternate.fraction.numerator
        fraction = (
            max_(
                0,
                min_(
                    alternate_numerator.min, alternate_numerator.top - ny_agi
                ),
            )
            / alternate.fraction.denominator
        )
        alternate_percentage = (
            alternate.base_percentage + fraction * alternate.multiplier
        )

        ny_percentage = where(
            ny_agi < alternate.max_agi,
            alternate_percentage,
            main_percentage,
        )

        s_1_b_multiplier = percentage.multiplier.calc(ny_agi)

        return ny_percentage * s_1_b_multiplier
