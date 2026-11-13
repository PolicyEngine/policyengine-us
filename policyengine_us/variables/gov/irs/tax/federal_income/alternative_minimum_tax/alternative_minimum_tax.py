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
        # 1. Tax on Foreign income (Foreign Earned Income Tax Worksheet)
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
        total_amt_tax = where(form_6251_part_iii_required, smaller_tax, amt_base_tax)

        # 26 U.S.C. 911(f)(1)(B): a taxpayer excluding foreign earned income
        # figures the taxes above on the taxable excess plus the excluded
        # amount, then subtracts the tax at the AMT rates on the excluded
        # amount alone (Form 6251 Foreign Earned Income Tax Worksheet, lines
        # 5 and 6). It applies only if there is a taxable excess.
        p = parameters(period).gov.irs.income.amt
        filing_status = tax_unit("filing_status", period)
        taxable_excess = tax_unit("amt_income_less_exemptions", period)
        excluded = where(
            taxable_excess > 0,
            max_(0, tax_unit("foreign_earned_income_exclusion", period)),
            0,
        )
        tax_rate_threshold = p.brackets.thresholds[-1] * p.multiplier[filing_status]
        tax_on_excluded = p.brackets.rates[0] * min_(
            excluded, tax_rate_threshold
        ) + p.brackets.rates[1] * max_(0, excluded - tax_rate_threshold)
        total_amt_tax = where(
            excluded > 0, max_(0, total_amt_tax - tax_on_excluded), total_amt_tax
        )

        # Form 6251, Part II bottom
        # Line 8
        foreign_tax_credit = tax_unit("foreign_tax_credit_potential", period)
        # Line 9
        reduced_tax = total_amt_tax - foreign_tax_credit
        # Line 10: Form 1040 line 16 less any tax from Form 4972, less the
        # foreign tax credit. Line 16 is the regular tax including the
        # capital gains tax, the same amount income_tax_before_credits adds.
        regular_tax_before_credits = tax_unit("regular_tax_before_credits", period)
        lump_sum_distributions = tax_unit("form_4972_lumpsum_distributions", period)
        reduced_tax_before_credits = max_(
            0,
            regular_tax_before_credits - foreign_tax_credit - lump_sum_distributions,
        )
        return max_(0, reduced_tax - reduced_tax_before_credits)
