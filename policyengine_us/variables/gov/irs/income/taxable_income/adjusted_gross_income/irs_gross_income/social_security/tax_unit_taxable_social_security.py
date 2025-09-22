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

        # Special case: Flat taxation with zero thresholds
        # When both thresholds are 0 and rates are equal, this becomes a flat tax
        # The standard formula breaks down because it uses "excess" which is based on
        # combined income (only includes 50% of SS), not the full SS amount
        is_flat_tax_case = (
            (base_amount == 0)
            & (adjusted_base_amount == 0)
            & (p.rate.base == p.rate.additional)
        )

        # For flat tax case, directly apply the rate to gross SS
        flat_tax_amount = p.rate.base * gross_ss

        # Standard IRC Section 86 calculation for non-flat cases
        # Calculate excesses
        excess_over_base = max_(0, combined_income - base_amount)
        excess_over_adjusted = max_(0, combined_income - adjusted_base_amount)

        # Tier 1: Between base and adjusted base thresholds
        # Taxable amount is lesser of:
        # - base_rate * SS benefits
        # - base_rate * excess over base
        tier1_taxable = min_(
            p.rate.base * gross_ss, p.rate.base * excess_over_base
        )

        # Tier 2: Above adjusted base threshold
        # Sum of:
        # (1) base_rate applied to the range between thresholds
        # (2) additional_rate applied to excess over adjusted base
        # But capped at additional_rate * gross_ss

        # Calculate the taxable amount from the first bracket
        bracket_width = adjusted_base_amount - base_amount

        # Base component depends on bracket width
        tier2_base_component = where(
            bracket_width <= 0,
            0,  # No intermediate bracket
            min_(p.rate.base * bracket_width, p.rate.base * gross_ss),
        )

        # Additional rate applies to excess over adjusted base
        tier2_additional_component = p.rate.additional * excess_over_adjusted

        # Total cannot exceed additional_rate * gross_ss
        tier2_taxable = min_(
            tier2_base_component + tier2_additional_component,
            p.rate.additional * gross_ss,
        )

        # Standard tiered calculation
        standard_amount = select(
            [
                combined_income <= base_amount,
                combined_income <= adjusted_base_amount,
                True,
            ],
            [
                0,
                tier1_taxable,
                tier2_taxable,
            ],
        )

        # Return flat tax amount for flat tax case, otherwise standard calculation
        return where(is_flat_tax_case, flat_tax_amount, standard_amount)
