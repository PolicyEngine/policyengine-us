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
        # Per IRC §86(a)(1), "the amount determined under paragraph (1)"
        # Taxable amount is lesser of:
        # - base.benefit_cap * SS benefits [§86(a)(1)(A)]
        # - base.excess * excess over base [§86(a)(1)(B)]
        amount_under_paragraph_1 = min_(
            p.rate.base.benefit_cap * gross_ss,
            p.rate.base.excess * combined_income_excess,
        )

        # Tier 2: Above adjusted base threshold
        # Per IRC §86(a)(2)(A)(ii), the lesser of:
        # - "the amount determined under paragraph (1)" (calculated above)
        # - "one-half of the difference between the adjusted base amount and the base amount"
        bracket_amount = min_(
            amount_under_paragraph_1,
            p.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )

        # Per IRC §86(a)(2), the lesser of:
        # (A) 85% of excess over adjusted base + bracket amount, or
        # (B) 85% of social security benefits
        amount_if_over_second_threshold = min_(
            p.rate.additional.excess * excess_over_adjusted_base
            + bracket_amount,
            p.rate.additional.benefit_cap * gross_ss,
        )

        return select(
            [
                under_first_threshold,
                under_second_threshold,
            ],
            [
                0,
                amount_under_paragraph_1,
            ],
            default=amount_if_over_second_threshold,
        )
