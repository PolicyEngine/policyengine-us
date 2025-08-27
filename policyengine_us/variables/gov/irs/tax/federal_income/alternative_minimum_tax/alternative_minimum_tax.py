from policyengine_us.model_api import *


class alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) liability"

    def formula(tax_unit, period, parameters):
        # Line 7 consists of 3 parts:
        # 1. Tax on Foreign income (not modelled)
        # 2. Tax on capital gains (Part III)
        # 3. Regular AMT tax
        # If Form 6251, Part III is required, the regular AMT tax is calculated
        # by using the smaller of the regular AMT tax calculated on the
        # reduced income or the tax on capital gains (Part III)
        # Regular AMT tax:
        amt_base_tax = tax_unit("amt_base_tax", period)

        # Tax on capital gains (Part III)
        form_6251_part_iii_required = tax_unit("amt_part_iii_required", period)

        amt_tax_including_cg = tax_unit("amt_tax_including_cg", period)
        smaller_tax = min_(amt_base_tax, amt_tax_including_cg)
        total_amt_tax = where(
            form_6251_part_iii_required, smaller_tax, amt_base_tax
        )

        # Form 6251, Part II bottom
        # Line 8
        foreign_tax_credit = tax_unit("foreign_tax_credit_potential", period)
        # Line 9
        reduced_tax = total_amt_tax - foreign_tax_credit
        # Line 10 contains regular tax before credits, lump sum distributions, and capital gains tax
        regular_tax_before_credits = tax_unit(
            "regular_tax_before_credits", period
        )
        lump_sum_distributions = tax_unit(
            "form_4972_lumpsum_distributions", period
        )
        capital_gains_tax = tax_unit("capital_gains_tax", period)
        tax_before_credits = regular_tax_before_credits + capital_gains_tax
        reduced_tax_before_credits = max_(
            0, tax_before_credits - foreign_tax_credit - lump_sum_distributions
        )
        return max_(0, reduced_tax - reduced_tax_before_credits)
