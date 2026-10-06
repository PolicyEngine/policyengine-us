from collections import namedtuple

from policyengine_us.model_api import *

FilerScheduleDLines = namedtuple(
    "FilerScheduleDLines", ["line_7", "line_15", "line_16"]
)


def filer_schedule_d_lines(tax_unit, period):
    """Schedule D (Form 1040) lines 7, 15 and 16 of the head and spouse, shared
    by the Form 1040 line 16 routing (has_qdiv_or_ltcg), net_capital_gain, the
    Schedule D Tax Worksheet and the 28% Rate Gain Worksheet.

    Line 7 is the net short-term capital gain or loss. Line 15 is the net
    long-term capital gain or loss, including capital gain distributions
    (line 13). Line 16 is lines 7 and 15 combined (2025 Schedule D, lines 7,
    13, 15 and 16).

    A tax unit dependent's gains, losses and distributions belong on the
    dependent's own return, so they are left out, as irs_gross_income leaves
    them out of adjusted gross income. Line 16 starts from net_capital_gains,
    so a tax unit amount supplied there is kept; that amount is read as
    covering every member, and any dependent's person-level gains and losses
    are then taken out.

    Capital gain distributions reported without Schedule D
    (non_sch_d_capital_gains) are long-term capital gains (26 U.S.C.
    852(b)(3)(B)) and go on line 13 when the filer files Schedule D (2025
    Instructions for Schedule D, "Capital Gain Distributions"). They are Form
    1099-DIV box 2a amounts, which are not negative, so each filer's input is
    floored at zero here, as irs_gross_income floors it.
    """
    person = tax_unit.members
    dependent = person("is_tax_unit_dependent", period)
    distributions = tax_unit.sum(
        ~dependent * max_(0, person("non_sch_d_capital_gains", period))
    )
    line_7 = tax_unit_non_dep_add(tax_unit, period, ["short_term_capital_gains"])
    line_15 = (
        tax_unit_non_dep_add(tax_unit, period, ["long_term_capital_gains"])
        + distributions
    )
    # Line 16: lines 7 and 15 combined, figured from net_capital_gains so a
    # supplied tax unit amount is kept.
    dependent_gains = tax_unit.sum(
        dependent
        * (
            person("long_term_capital_gains", period)
            + person("short_term_capital_gains", period)
        )
    )
    line_16 = tax_unit("net_capital_gains", period) - dependent_gains + distributions
    return FilerScheduleDLines(line_7=line_7, line_15=line_15, line_16=line_16)
