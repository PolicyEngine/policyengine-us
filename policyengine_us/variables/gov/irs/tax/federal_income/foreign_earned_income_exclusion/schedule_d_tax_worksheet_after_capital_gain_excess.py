from collections import namedtuple

from policyengine_us.model_api import *

ScheduleDTaxWorksheet = namedtuple(
    "ScheduleDTaxWorksheet",
    [
        "capital_gain_excess",
        "line_9",
        "line_10",
        "line_13",
        "unrecaptured_section_1250_gain",
    ],
)


def schedule_d_tax_worksheet_after_capital_gain_excess(tax_unit, period, taxable_base):
    """Schedule D Tax Worksheet amounts refigured for a capital gain excess.

    `taxable_base` is taxable income (Form 1040 line 15) for the regular tax
    and Form 6251 line 6 for the AMT. A Form 2555 filer has a capital gain
    excess when worksheet line 10 is more than it, and then completes the
    worksheet a second time with four modifications, which carry out 26
    U.S.C. 911(f)(2):
    1. line 9 is reduced, but not below zero, by the excess;
    2. line 6 is reduced, but not below zero, by the excess not used in (1);
    3. Schedule D line 18 (28% rate gain) is reduced, but not below zero, by
       the excess;
    4. the excess enters line 16 of the Unrecaptured Section 1250 Gain
       Worksheet as a loss, which reduces Schedule D line 19 by the part of
       the excess the 28% rate gain did not absorb.
    Sources: 2025 Form 1040 instructions, Foreign Earned Income Tax
    Worksheet—Line 16, footnote; 2025 Form 6251 instructions, Part III,
    "Form 2555".

    The excess is measured as the worksheets measure it, from line 10 (the
    statute's net capital gain, which section_911_capital_gain_excess uses for
    the section 1(h) formulas, can differ from line 10 when investment income
    elections or capital gain distributions are entered).

    Returns the excess, worksheet lines 9, 10 and 13 and Schedule D line 19.
    Without an excess these are the first worksheet's amounts, unchanged.
    """
    line_9 = tax_unit("dwks09", period)
    line_10 = tax_unit("dwks10", period)
    line_13 = tax_unit("dwks13", period)
    excludes_income = tax_unit("foreign_earned_income_exclusion", period) > 0
    capital_gain_excess = where(
        excludes_income, max_(0, line_10 - max_(0, taxable_base)), 0
    )
    has_excess = capital_gain_excess > 0
    unrecaptured_gain = tax_unit("unrecaptured_section_1250_gain", period)
    rate_gain = tax_unit("capital_gains_28_percent_rate_gain", period)
    # Modifications 1 and 2.
    reduced_line_9 = max_(0, line_9 - capital_gain_excess)
    excess_after_line_9 = max_(0, capital_gain_excess - line_9)
    line_6 = tax_unit("dividend_income_reduced_by_investment_income", period)
    reduced_line_6 = max_(0, line_6 - excess_after_line_9)
    reduced_line_10 = reduced_line_6 + reduced_line_9
    # Modifications 3 and 4. section_911_28_percent_rate_gain and
    # section_911_unrecaptured_section_1250_gain apply the regular tax excess;
    # this helper also runs with the AMT excess, so it applies them itself.
    reduced_rate_gain = max_(0, rate_gain - capital_gain_excess)
    reduced_unrecaptured_gain = max_(
        0, unrecaptured_gain - max_(0, capital_gain_excess - rate_gain)
    )
    # Lines 11 to 13, as in dwks13.
    reduced_line_11 = reduced_unrecaptured_gain + reduced_rate_gain
    reduced_line_12 = min_(reduced_line_9, reduced_line_11)
    reduced_line_13 = (reduced_line_10 - reduced_line_12) * tax_unit(
        "has_qdiv_or_ltcg", period
    )
    return ScheduleDTaxWorksheet(
        capital_gain_excess=capital_gain_excess,
        line_9=where(has_excess, reduced_line_9, line_9),
        line_10=where(has_excess, reduced_line_10, line_10),
        line_13=where(has_excess, reduced_line_13, line_13),
        unrecaptured_section_1250_gain=where(
            has_excess, reduced_unrecaptured_gain, unrecaptured_gain
        ),
    )
