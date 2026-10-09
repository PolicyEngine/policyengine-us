from collections import namedtuple

from policyengine_us.model_api import *

FilerScheduleDLines = namedtuple(
    "FilerScheduleDLines", ["line_7", "line_15", "line_16"]
)


def filer_schedule_d_lines(tax_unit, period):
    """Schedule D (Form 1040) lines 7, 15 and 16 of the head and spouse, shared
    by Form 1040 line 7a (filer_loss_limited_net_capital_gains), the line 16
    routing (has_qdiv_or_ltcg), net_capital_gain and the Schedule D Tax
    Worksheet.

    Line 7 is the net short-term capital gain or loss. Line 15 is the net
    long-term capital gain or loss, including capital gain distributions
    (line 13). With component-derived inputs, line 16 is lines 7 and 15
    combined (2025 Schedule D, lines 7, 13, 15 and 16).

    A tax unit dependent's gains, losses and distributions belong on the
    dependent's own return, so they are left out, as irs_gross_income leaves
    them out of adjusted gross income. Line 16 combines the filers' lines 7
    and 15 directly, so a large dependent's gain cannot round away a filer's
    smaller gain in the float32 tax unit aggregate. When net_capital_gains
    differs from the computed all-member aggregate in its storage precision,
    that supplied amount covers every member, so dependents' own gains and
    losses are removed before the filers' distributions are added. An amount
    equal to the computed aggregate uses the direct filer components.
    An explicit aggregate override can make line 16 differ from lines 7 and
    15 combined, and the worksheet and statutory net-capital-gain paths can
    then disagree.

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
    # A component-derived aggregate may have rounded away a filer's dollar,
    # so sum the filers directly when it matches its normal stored value.
    # A differing supplied aggregate covers every member: subtract the
    # dependents directly instead of reconciling it through a rounded total.
    net_capital_gains = tax_unit("net_capital_gains", period)
    computed_gains = add(
        tax_unit, period, ["long_term_capital_gains", "short_term_capital_gains"]
    ).astype(net_capital_gains.dtype)
    dependent_gains = tax_unit.sum(
        dependent * person("long_term_capital_gains", period)
    ) + tax_unit.sum(dependent * person("short_term_capital_gains", period))
    line_16 = where(
        net_capital_gains == computed_gains,
        line_7 + line_15,
        net_capital_gains.astype(float) - dependent_gains + distributions,
    )
    return FilerScheduleDLines(line_7=line_7, line_15=line_15, line_16=line_16)
