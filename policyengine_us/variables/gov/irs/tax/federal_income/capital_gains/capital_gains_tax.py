from numpy import clip
from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.section_911_net_capital_gain_other_than_dividends import (
    section_911_net_capital_gain_other_than_dividends,
)


def rate_gain_taxed_at_28_percent(
    tax_unit,
    period,
    taxable_income,
    regular_rate_income,
    adjusted_net_capital_gain,
    taxed_unrecaptured_gain,
):
    """The amount 26 U.S.C. 1(h)(1)(F) taxes at 28 percent.

    Subparagraph (F) taxes "the amount of taxable income in excess of the
    sum of the amounts on which tax is determined under the preceding
    subparagraphs" (Schedule D Tax Worksheet lines 41 and 42): taxable
    income less the regular rate amount (A), the adjusted net capital gain or
    taxable income if less, which (B) to (D) tax between them, and the
    unrecaptured section 1250 gain (E) taxes. That is the 28 percent rate gain
    less any of it (A) taxes at the regular rates, which happens when it falls
    in the brackets below 25 percent. The excess is never more than the 28
    percent rate gain; taking the smaller also keeps rounding from taxing a
    household without it.
    """
    return min_(
        tax_unit("section_911_28_percent_rate_gain", period),
        max_(
            0,
            taxable_income
            - regular_rate_income
            - adjusted_net_capital_gain
            - taxed_unrecaptured_gain,
        ),
    )


class capital_gains_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum income tax after capital gains tax"
    unit = USD
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1",
        ),
        dict(
            title="26 U.S. Code § 911(f)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # A taxpayer excluding foreign earned income applies section 1(h) to
        # taxable income plus the excluded amount, with gains reduced by any
        # capital gain excess (26 U.S.C. 911(f)). Everyone else's amounts are
        # unchanged.
        net_cg = tax_unit("section_911_net_capital_gain", period)
        taxable_income = tax_unit("taxable_income_plus_section_911_exclusion", period)
        adjusted_net_cg = min_(
            tax_unit("section_911_adjusted_net_capital_gain", period),
            taxable_income,
        )  # ANCG is referred to in all cases as ANCG or taxable income if less.

        cg = parameters(period).gov.irs.capital_gains

        excluded_cg = tax_unit("capital_gains_excluded_from_taxable_income", period)
        non_cg_taxable_income = max_(0, taxable_income - excluded_cg)
        income_less_ancg = max_(0, taxable_income - adjusted_net_cg)

        filing_status = tax_unit("filing_status", period)

        first_threshold = cg.thresholds["1"][filing_status]
        second_threshold = cg.thresholds["2"][filing_status]

        income_ordinarily_under_second_rate = clip(taxable_income, 0, first_threshold)
        cg_in_first_bracket = max_(
            0, income_ordinarily_under_second_rate - income_less_ancg
        )

        income_ordinarily_under_third_rate = clip(taxable_income, 0, second_threshold)
        cg_in_second_bracket = min_(
            max_(0, adjusted_net_cg - cg_in_first_bracket),
            max_(
                0,
                income_ordinarily_under_third_rate
                - (non_cg_taxable_income + cg_in_first_bracket),
            ),
        )

        cg_in_third_bracket = max_(
            adjusted_net_cg - cg_in_first_bracket - cg_in_second_bracket,
            0,
        )

        main_cg_tax = (
            cg_in_first_bracket * cg.rates["1"]
            + cg_in_second_bracket * cg.rates["2"]
            + cg_in_third_bracket * cg.rates["3"]
        )

        unrecaptured_s_1250_gain = tax_unit(
            "section_911_unrecaptured_section_1250_gain", period
        )
        # Net capital gain determined without regard to section 1(h)(11),
        # reduced first by any capital gain excess (26 U.S.C.
        # 911(f)(2)(A)(i)).
        net_cg_other_than_dividends = section_911_net_capital_gain_other_than_dividends(
            tax_unit, period
        )
        max_taxable_unrecaptured_gain = min_(
            unrecaptured_s_1250_gain,
            net_cg_other_than_dividends,
        )
        unrecaptured_gain_deduction = max_(
            non_cg_taxable_income + net_cg - taxable_income,
            0,
        )
        taxable_unrecaptured_gain = max_(
            max_taxable_unrecaptured_gain - unrecaptured_gain_deduction,
            0,
        )

        unrecaptured_gain_tax = cg.unrecaptured_s_1250_rate * taxable_unrecaptured_gain

        # 26 U.S.C. 1(h)(1)(F): 28 percent of the rest of taxable income.
        remaining_cg_tax = cg.other_cg_rate * rate_gain_taxed_at_28_percent(
            tax_unit,
            period,
            taxable_income,
            non_cg_taxable_income,
            adjusted_net_cg,
            taxable_unrecaptured_gain,
        )

        return main_cg_tax + unrecaptured_gain_tax + remaining_cg_tax
