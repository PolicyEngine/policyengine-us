from policyengine_us.model_api import *


class taxsim_v12(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social Security in AGI"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("taxsim_gssi", period)

        combined_income = (
            tax_unit("taxable_ss_magi", period)
            + p.combined_income_ss_fraction * gross_ss
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
        combined_income_excess = max_(0, combined_income - base_amount)
        excess_over_adjusted_base = max_(0, combined_income - adjusted_base_amount)

        amount_under_paragraph_1 = min_(
            p.rate.base.benefit_cap * gross_ss,
            p.rate.base.excess * combined_income_excess,
        )
        bracket_amount = min_(
            amount_under_paragraph_1,
            p.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )
        amount_if_over_second_threshold = min_(
            p.rate.additional.excess * excess_over_adjusted_base + bracket_amount,
            p.rate.additional.benefit_cap * gross_ss,
        )

        return select(
            [under_first_threshold, under_second_threshold],
            [0, amount_under_paragraph_1],
            default=amount_if_over_second_threshold,
        )
