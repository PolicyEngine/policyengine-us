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

    Lines 3 and 4 are the Form 4952 amounts the investment interest deduction
    uses: form_4952_elected_investment_income, the head's and spouse's
    election capped at Form 4952 lines 4b plus 4e, and
    form_4952_net_capital_gain. Those variables compute their gains directly
    and never read this worksheet. The model has no input for the "Elec."
    amount a taxpayer may write next to line 4e (the worksheet's line 4
    footnote), so the election is attributed first to net capital gain and
    then to qualified dividends, as the line 4g instructions do by default.

    Line 7 keeps the Schedule D amounts the rest of the capital gains tax
    uses. Capital gain distributions reported without Schedule D
    (non_sch_d_capital_gains) belong on Schedule D line 13 (2025 Instructions
    for Schedule D, "Capital Gain Distributions"), so they enter lines 15 and
    16.
    """
    long_term_gains = add(tax_unit, period, ["long_term_capital_gains"])
    distributions = add(tax_unit, period, ["non_sch_d_capital_gains"])
    # Schedule D line 15 (net long-term gain or loss, with line 13) and line
    # 16 (Schedule D line 7 plus line 15).
    schedule_d_line_15 = long_term_gains + distributions
    schedule_d_line_16 = tax_unit("net_capital_gains", period) + distributions
    return ScheduleDTaxWorksheetForm4952Lines(
        line_3=tax_unit("form_4952_elected_investment_income", period),
        line_4=tax_unit("form_4952_net_capital_gain", period),
        line_7=min_(schedule_d_line_15, schedule_d_line_16),
    )
