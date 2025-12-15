from policyengine_us.model_api import *


class taxable_social_security_tier_1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security (tier 1)"
    documentation = "Taxable Social Security from 0-50% taxation tier, credited to OASDI trust funds"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#a_1"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)
        combined_income = tax_unit(
            "tax_unit_combined_income_for_social_security_taxability", period
        )
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)

        base_amount = where(
            separate & cohabitating,
            p.threshold.base.separate_cohabitating,
            p.threshold.base.main[filing_status],
        )
        adjusted_base_amount = where(
            separate & cohabitating,
            p.threshold.adjusted_base.separate_cohabitating,
            p.threshold.adjusted_base.main[filing_status],
        )

        under_first_threshold = combined_income < base_amount
        under_second_threshold = combined_income < adjusted_base_amount

        combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )

        # Tier 1 amount (IRC §86(a)(1))
        amount_under_paragraph_1 = min_(
            p.rate.base.benefit_cap * gross_ss,
            p.rate.base.excess * combined_income_excess,
        )

        # Bracket amount when in tier 2 (IRC §86(a)(2)(A)(ii))
        bracket_amount = min_(
            amount_under_paragraph_1,
            p.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )

        return select(
            [under_first_threshold, under_second_threshold],
            [0, amount_under_paragraph_1],
            default=bracket_amount,
        )
