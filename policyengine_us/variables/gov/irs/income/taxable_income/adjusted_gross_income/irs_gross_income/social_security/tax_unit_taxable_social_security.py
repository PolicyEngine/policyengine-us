from policyengine_us.model_api import *


class tax_unit_taxable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security benefits"
    documentation = "Social security (OASDI) benefits included in AGI, including tier 1 railroad retirement benefits."
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)

        # The legislation directs the usage an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. We assume that the 'half' here is the same underlying
        # parameter as the lower taxability marginal rate (also 50% in the
        # baseline), and that they would be mechanically the same parameter.

        combined_income = tax_unit(
            "tax_unit_combined_income_for_social_security_taxability", period
        )
        filing_status = tax_unit("filing_status", period)

        base_amount = p.threshold.lower[filing_status]
        adjusted_base_amount = p.threshold.upper[filing_status]

        under_first_threshold = combined_income < base_amount
        under_second_threshold = combined_income < adjusted_base_amount

        combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )
        excess_over_adjusted_base = max_(
            0, combined_income - adjusted_base_amount
        )

        amount_if_under_second_threshold = p.rate.lower * min_(
            combined_income_excess, gross_ss
        )
        amount_if_over_second_threshold = min_(
            p.rate.upper * excess_over_adjusted_base
            + min_(
                amount_if_under_second_threshold,
                p.rate.lower * (adjusted_base_amount - base_amount),
            ),
            p.rate.upper * gross_ss,
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
