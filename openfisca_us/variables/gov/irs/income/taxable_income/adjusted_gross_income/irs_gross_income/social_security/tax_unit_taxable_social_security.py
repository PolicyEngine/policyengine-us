from openfisca_us.model_api import *


class tax_unit_taxable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security benefits"
    documentation = "Social security (OASDI) benefits included in AGI"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    def formula(tax_unit, period, parameters):
        ss = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)

        # The legislation directs the usage an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. We assume that the 'half' here is the same underlying
        # parameter as the lower taxability marginal rate (also 50% in the
        # baseline), and that they would be mechanically the same parameter.

        ss_fraction = ss.rate.lower * gross_ss
        modified_agi_plus_half_ss = (
            tax_unit("taxable_ss_magi", period) + ss_fraction
        )
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
