from collections import namedtuple

from policyengine_us.model_api import *

ScheduleDTaxWorksheetForm4952Lines = namedtuple(
    "ScheduleDTaxWorksheetForm4952Lines", ["line_3", "line_4", "line_7"]
)


def schedule_d_tax_worksheet_form_4952_lines(tax_unit, period):
    """Schedule D Tax Worksheet lines 3, 4 and 7 (2025 Instructions for
    Schedule D, page 15), shared by dwks09 and
    dividend_income_reduced_by_investment_income.

    Line 3 is Form 4952 line 4g, the net capital gain and qualified dividends
    the taxpayer elects to include in investment income (26 U.S.C.
    163(d)(4)(B)). Line 4 is Form 4952 line 4e, "the smaller of line 4d or
    your net capital gain from the disposition of property held for
    investment". Line 7 is "the smaller of line 15 or line 16 of Schedule D".

    The model treats every capital asset as property held for investment, so
    Form 4952 line 4d is the excess of total gains over total losses and
    line 4e's net capital gain is the excess of net long-term capital gain
    over net short-term capital loss (2025 Form 4952 instructions, lines 4d
    and 4e). It has no input for the "Elec." amount a taxpayer may write next
    to line 4e (the worksheet's line 4 footnote), so the election is
    attributed first to net capital gain and then to qualified dividends, as
    the line 4g instructions do by default.

    Capital gain distributions reported without Schedule D
    (non_sch_d_capital_gains) belong on Schedule D line 13 (2025 Instructions
    for Schedule D, "Capital Gain Distributions"), so they enter lines 15 and
    16, and Form 4952 counts them as long-term capital gains.
    """
    election = max_(0, add(tax_unit, period, ["investment_income_elected_form_4952"]))
    long_term_gains = add(tax_unit, period, ["long_term_capital_gains"])
    short_term_gains = add(tax_unit, period, ["short_term_capital_gains"])
    distributions = add(tax_unit, period, ["non_sch_d_capital_gains"])
    # Schedule D line 15 (net long-term gain or loss, with line 13) and line
    # 16 (Schedule D line 7 plus line 15).
    schedule_d_line_15 = long_term_gains + distributions
    schedule_d_line_16 = tax_unit("net_capital_gains", period) + distributions
    # Form 4952 line 4d: total gains over total losses, if any.
    net_gain = max_(0, schedule_d_line_16)
    # Net capital gain from property held for investment: net long-term
    # capital gain over net short-term capital loss, if any.
    net_capital_gain = max_(0, schedule_d_line_15 - max_(0, -short_term_gains))
    return ScheduleDTaxWorksheetForm4952Lines(
        line_3=election,
        line_4=min_(net_gain, net_capital_gain),
        line_7=min_(schedule_d_line_15, schedule_d_line_16),
    )
