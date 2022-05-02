from openfisca_us.model_api import *


class taxable_ss(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable social security benefits"
    documentation = "Social security (OASDI) benefits included in AGI"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    def formula(tax_unit, period, parameters):
        ss = parameters(period).irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_ss", period)
        modified_agi_plus_half_ss = tax_unit(
            "ymod", period
        )  # Defined in 26 U.S.C § 86(b)(2)
        filing_status = tax_unit("filing_status", period)

        base_amount = ss.threshold.lower[filing_status]
        adjusted_base_amount = ss.threshold.upper[filing_status]

        under_first_threshold = modified_agi_plus_half_ss < base_amount
        under_second_threshold = (
            modified_agi_plus_half_ss < adjusted_base_amount
        )

        excess_over_base = max_(0, modified_agi_plus_half_ss - base_amount)
        excess_over_adjusted_base = max_(
            0, modified_agi_plus_half_ss - adjusted_base_amount
        )

        amount_if_under_second_threshold = ss.rate.lower * min_(
            excess_over_base, gross_ss
        )
        amount_if_over_second_threshold = min_(
            ss.rate.upper * excess_over_adjusted_base
            + min_(
                amount_if_under_second_threshold,
                ss.rate.lower * (adjusted_base_amount - base_amount),
            ),
            ss.rate.upper * gross_ss,
        )
        return select(
            [
                under_first_threshold,
                under_second_threshold,
                True,
            ],
            [
                0,
                amount_if_under_second_threshold,
                amount_if_over_second_threshold,
            ],
        )


c02500 = variable_alias("c02500", taxable_ss)
