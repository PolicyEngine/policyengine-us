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

        # The legislation directs the usage of an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. Per IRC Section 86(b)(1), this fraction is always 0.5
        # and is handled by the combined_income_ss_fraction parameter.

        combined_income = tax_unit(
            "tax_unit_combined_income_for_social_security_taxability", period
        )
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        # Cohabitating married couples filing separately receive a base
        # and adjusted base amount of 0
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
        excess_over_adjusted_base = max_(
            0, combined_income - adjusted_base_amount
        )

        # Tier 1: Between base and adjusted base thresholds
        # Taxable amount is lesser of:
        # - tier1_benefit_cap * SS benefits
        # - tier1_excess * excess over base
        amount_if_under_second_threshold = min_(
            p.rate.tier1_benefit_cap * gross_ss,
            p.rate.tier1_excess * combined_income_excess
        )

        # Tier 2: Above adjusted base threshold
        # Sum of:
        # (1) tier1_bracket rate applied to the range between thresholds
        # (2) tier2_excess rate applied to excess over adjusted base
        # But capped at tier2_benefit_cap * gross_ss
        bracket_amount = min_(
            p.rate.tier1_bracket * (adjusted_base_amount - base_amount),
            p.rate.tier1_bracket * gross_ss
        )

        amount_if_over_second_threshold = min_(
            p.rate.tier2_excess * excess_over_adjusted_base + bracket_amount,
            p.rate.tier2_benefit_cap * gross_ss
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
