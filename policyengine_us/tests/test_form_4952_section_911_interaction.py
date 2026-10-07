"""Property tests for a Form 4952 election together with section 911(f).

A taxpayer may elect, on Form 4952 line 4g, to treat net capital gain and
qualified dividends as investment income (26 U.S.C. 163(d)(4)(B)); the
elected amounts lose the capital gains rates (section 1(h)(2) and
1(h)(11)(D)(i)). A taxpayer who excludes foreign earned income under section
911(a) pays tax on the rest at the rates it would bear on top of the excluded
amount, and any capital gain excess is taken from the gains first (section
911(f)). test_form_4952_election_worksheet.py checks the election without an
exclusion, and test_section_911_tax_stacking.py the exclusion without an
election. This file checks households with both.

On a return the two meet in the Schedule D Tax Worksheet, which a filer with
an amount on Form 4952 line 4g must use (2025 Instructions for Schedule D,
page 15). The Foreign Earned Income Tax Worksheet measures the capital gain
excess from worksheet line 10 and takes it from line 9 before line 6 (2025
Instructions for Form 1040, page 37; the AMT does the same with Form 6251
line 6, 2025 Instructions for Form 6251, Part III, "Form 2555"). The model
reaches these amounts by two routes: the worksheet (dwks09, dwks10,
schedule_d_tax_worksheet_after_capital_gain_excess) and section 1(h)
(net_capital_gain and the section_911_* variables).

Write G for the gain of section 1222(11) (net long-term gain, with capital
gain distributions, less net short-term loss, if positive), D for qualified
dividends, E for the election, X for the exclusion, T for taxable income and
N = max(0, G - E) + max(0, D - max(0, E - G)), the net capital gain the
election leaves. The properties, for every generated household:

1. Closed forms. net_capital_gain and dwks10 are N; worksheet line 6 is
   min(D, N). Without an exclusion the section 911 amounts are the originals.
   With one, the capital gain excess is max(0, N - T),
   section_911_net_capital_gain is min(N, T) and
   section_911_qualified_dividend_income is min(D, N, T). Without an excess,
   section_911_qualified_dividend_income is min(D, net_capital_gain), bit for
   bit. The gain other than dividends plus those dividends is
   section_911_net_capital_gain.
2. The two routes agree. The worksheet's capital gain excess, line 10, line
   9, line 10 less line 9, line 13 and Schedule D line 19 equal the section
   1(h) excess, net capital gain, gain other than dividends, qualified
   dividends, adjusted net capital gain and unrecaptured section 1250 gain,
   and lines 6 and 9 after the excess equal modifications 1 and 2 of the
   Foreign Earned Income Tax Worksheet footnote applied to the transcribed
   worksheet. The AMT excess is max(0, N - max(0, Form 6251 line 6)).
3. Zero amounts change nothing. A household that elects nothing gets the
   same results, bit for bit, as when the situation has no election input
   (the situation of test_section_911_tax_stacking.py), and one that excludes
   nothing the same as when it has no exclusion input (that of
   test_form_4952_election_worksheet.py), whatever the other households in
   the batch elect or exclude. With no capital gain excess, every amount that
   section 911(f) replaces equals its original, bit for bit.
4. Monotonicity. E changes taxable income only through the choice to
   itemize (see assert_monotone). X can also reduce the SALT deduction
   through its modified AGI add-back, raising taxable income even while
   the choice holds. As E rises, net_capital_gain and dwks10
   never rise, and net capital gain falls by at most the extra amount
   elected. While the choice to itemize holds, the section 911 net capital
   gain and qualified dividends and both capital gain excesses never rise
   either. As X rises the regular tax and income_tax_before_credits never
   fall while the choice holds, and stacking never lowers them. income_tax,
   which the choice minimizes, never falls as X rises, whatever the choice,
   for households without dependents.
   The tax does not always rise with E: from the 0% capital gains threshold
   to the top of the 12% bracket (2025: $48,350 to $48,475 single), gain is
   taxed at 15% and ordinary income at 12%, so a dollar elected there lowers
   the tax by 3 cents, on the return as in the model
   (test_election_can_lower_the_tax_where_15_percent_exceeds_12). The tax
   (each of the three) falls by at most the 3 points times the width of that
   band ($3.75 single, $7.50 joint in 2025), which `rate_overlap` computes
   from the parameters.
5. Worksheet lines. dwks10 equals net_capital_gain exactly for whole-dollar
   amounts and within single-precision rounding for amounts with cents; the
   model's lines 6, 9 and 10 equal the transcription in
   test_form_4952_election_worksheet.py.
6. End to end, against the 2025 forms. Schedule D Tax Worksheet lines 2 to
   10 (transcribed in test_form_4952_election_worksheet.py) feed the Foreign
   Earned Income Tax Worksheet and Form 6251 line 7 (transcribed in
   test_section_911_tax_stacking.py). With Schedule D lines 18 and 19 zero,
   Schedule D Tax Worksheet lines 14 to 47 are the Qualified Dividends and
   Capital Gain Tax Worksheet with worksheet line 6 for its line 2 and line 9
   for its line 3, and Form 6251 line 27 equals line 20. The model's regular
   tax and AMT match.

Amounts are whole dollars below 2**24 except where a household is drawn with
cents. For every whole-dollar household the gains and the model's worksheet
lines 6 to 10 hold exactly; the section 911 amounts hold exactly when taxable
income (or Form 6251 line 6) is whole dollars too, as taxable income is
without itemized deductions. The rest are checked within single-precision
rounding.

The scope limits of test_section_911_tax_stacking.py apply to the tax
comparisons (properties 4 and 6), which therefore use households without
28-percent rate gain or unrecaptured section 1250 gain. The model omits the
section 1(h)(1) cap at the tax on all taxable income at ordinary rates. It
uses the 26%/28% breakpoint of other filers for married filing separately on
Form 6251 line 18. And capital_gains_tax taxes 28-percent rate gain at 28% in
full, even where it exceeds taxable income or the net capital gain an election
leaves (Schedule D Tax Worksheet line 12 limits it to line 9): $10,000 of
collectibles gain and no taxable income gives $2,800 of tax. The households
are 45, so the exclusion does not reach the senior deduction.
"""

import numpy as np
import pytest
from policyengine_core.periods import period as make_period

from policyengine_us import Simulation
from policyengine_us.tests.test_form_4952_election_worksheet import (
    schedule_d_tax_worksheet,
)
from policyengine_us.tests.test_section_911_tax_stacking import (
    STATUSES,
    foreign_earned_income_tax_worksheet,
    form_6251_line_7,
    qualified_dividends_and_capital_gain_tax_worksheet,
    reduce_by_capital_gain_excess,
    tax_rate_schedule,
    tolerance,
)
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.section_911_net_capital_gain_other_than_dividends import (
    section_911_net_capital_gain_other_than_dividends,
)

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEARS = [2018, 2022, 2025, 2026]

# ---------------------------------------------------------------------------
# The law, in closed form.
# ---------------------------------------------------------------------------


def section_1222_gain(h):
    """Net long-term capital gain (capital gain distributions included) over
    net short-term capital loss, if positive: 26 U.S.C. 1222(11), before
    section 1(h)(11). It is also Form 4952 line 4e, worksheet line 4."""
    long_term = h["long_term"] + h["distributions"]
    return max(0, long_term - max(0, -h["short_term"]))


def net_capital_gain_after_election(h):
    """The election comes first from the gain and then from qualified
    dividends (2025 Form 4952, line 4g instructions)."""
    gain = section_1222_gain(h)
    dividends = max(0, h["dividends"])
    return max(0, gain - h["election"]) + max(
        0, dividends - max(0, h["election"] - gain)
    )


def rate_overlap(parameters, status):
    """How far the regular tax can fall when more gain is taxed at ordinary
    rates: the integral over income of the excess, where positive, of the
    capital gains rate over the ordinary rate. Moving a dollar of gain into
    ordinary income at income level x changes the tax by the ordinary rate
    less the capital gains rate at x."""
    bracket = parameters.gov.irs.income.bracket
    gains = parameters.gov.irs.capital_gains
    count = len(list(bracket.rates.__iter__()))
    ordinary = [
        (float(bracket.thresholds[str(i)][status]), float(bracket.rates[str(i)]))
        for i in range(1, count + 1)
    ]
    capital_gains = [
        (float(gains.thresholds["1"][status]), float(gains.rates["1"])),
        (float(gains.thresholds["2"][status]), float(gains.rates["2"])),
        (np.inf, float(gains.rates["3"])),
    ]

    def rate(schedule, x):
        return next(r for top, r in schedule if x < top)

    edges = sorted({0.0} | {top for top, _ in ordinary + capital_gains})
    overlap = 0.0
    for bottom, top in zip(edges, edges[1:]):
        middle = bottom + 1 if np.isinf(top) else (bottom + top) / 2
        excess = rate(capital_gains, middle) - rate(ordinary, middle)
        if excess > 0:
            assert np.isfinite(top), status
            overlap += excess * (top - bottom)
    return overlap


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------

OUTPUTS = [
    "taxable_income",
    "net_capital_gain",
    "dividend_income_reduced_by_investment_income",
    "dwks09",
    "dwks10",
    "dwks13",
    "adjusted_net_capital_gain",
    "unrecaptured_section_1250_gain",
    "capital_gains_28_percent_rate_gain",
    "foreign_earned_income_exclusion",
    "section_911_capital_gain_excess",
    "section_911_net_capital_gain",
    "section_911_qualified_dividend_income",
    "section_911_adjusted_net_capital_gain",
    "section_911_28_percent_rate_gain",
    "section_911_unrecaptured_section_1250_gain",
    "taxable_income_plus_section_911_exclusion",
    "amt_income_less_exemptions",
    "amt_income_less_exemptions_plus_section_911_exclusion",
    "amt_section_911_capital_gain_excess",
    "income_tax_main_rates",
    "capital_gains_tax",
    "regular_tax_before_credits",
    "alternative_minimum_tax",
    "income_tax_before_credits",
    "tax_unit_itemizes",
    "itemized_taxable_income_deductions",
    "agi_plus_section_911_931_933_exclusions",
    "salt_cap",
    "salt_deduction",
    "income_tax",
]


def split(amount, joint):
    """The head's and the spouse's shares. Joint filers split dividends and
    the election, so the model has to add them over the tax unit."""
    if not joint:
        return amount, 0
    spouse = amount // 2 if float(amount).is_integer() else round(amount / 2, 2)
    return amount - spouse, spouse


def build_situation(households, year, with_election=True, with_exclusion=True):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        joint = h["status"] == "JOINT"
        dividends = split(h["dividends"], joint)
        election = split(h["election"], joint)
        head = f"head_{i}"
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: h["wages"]},
            "qualified_dividend_income": {year: dividends[0]},
            "long_term_capital_gains": {year: h["long_term"]},
            "short_term_capital_gains": {year: h["short_term"]},
            "non_sch_d_capital_gains": {year: h["distributions"]},
            "real_estate_taxes": {year: h["real_estate_taxes"]},
            "deductible_mortgage_interest": {year: h["mortgage_interest"]},
            "charitable_cash_donations": {year: h["charitable_gifts"]},
        }
        if with_election:
            people[head]["investment_income_elected_form_4952"] = {year: election[0]}
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if joint:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {year: 45},
                "qualified_dividend_income": {year: dividends[1]},
            }
            if with_election:
                people[spouse]["investment_income_elected_form_4952"] = {
                    year: election[1]
                }
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["status"] == "HEAD_OF_HOUSEHOLD":
            # Old enough to be a dependent without a child tax credit.
            child = f"child_{i}"
            people[child] = {"age": {year: 17}}
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            # Set for every tax unit, as in test_section_911_tax_stacking.py.
            "filing_status": {year: h["status"]},
            "unrecaptured_section_1250_gain": {year: h["section_1250"]},
            "capital_gains_28_percent_rate_gain": {year: h["rate_gain_28"]},
        }
        if with_exclusion:
            tax_units[f"tax_unit_{i}"]["foreign_earned_income_exclusion"] = {
                year: h["exclusion"]
            }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def calculate(households, year, with_election=True, with_exclusion=True):
    simulation = Simulation(
        situation=build_situation(households, year, with_election, with_exclusion)
    )
    results = {v: np.asarray(simulation.calculate(v, year)) for v in OUTPUTS}
    results["filing_status"] = simulation.calculate(
        "filing_status", year
    ).decode_to_str()
    results["qualified_dividends"] = np.asarray(
        simulation.calculate("qualified_dividend_income", year, map_to="tax_unit")
    )
    results["regular_tax"] = (
        results["income_tax_main_rates"] + results["capital_gains_tax"]
    )
    tax_unit = simulation.populations["tax_unit"]
    period = make_period(year)
    results["gain_other_than_dividends"] = np.asarray(
        section_911_net_capital_gain_other_than_dividends(tax_unit, period)
    )
    # The worksheet refigured for the regular tax (taxable income) and the
    # AMT (Form 6251 line 6).
    for prefix, base in [
        ("worksheet", "taxable_income"),
        ("amt_worksheet", "amt_income_less_exemptions"),
    ]:
        worksheet = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, results[base]
        )
        for line in worksheet._fields:
            results[f"{prefix}_{line}"] = np.asarray(getattr(worksheet, line))
    parameters = simulation.tax_benefit_system.parameters(period.start)
    overlaps = {
        status: rate_overlap(parameters, str(status))
        for status in set(results["filing_status"])
    }
    results["rate_overlap"] = np.array(
        [overlaps[status] for status in results["filing_status"]]
    )
    return results


def column(households, key):
    return np.array([h[key] for h in households], dtype=float)


def rounding(scale):
    """Four units in the last place of single precision at `scale`: the
    rounding of a few stored amounts of that size."""
    return 4 * np.spacing(np.abs(np.asarray(scale)).astype(np.float32)).astype(float)


def assert_close(actual, expected, exact, scale, label):
    """Equal where `exact`, within single-precision rounding elsewhere."""
    actual = np.asarray(actual, dtype=float)
    expected = np.asarray(expected, dtype=float)
    slack = np.where(exact, 0.0, rounding(scale))
    bad = np.flatnonzero(np.abs(actual - expected) > slack)
    assert not bad.size, (label, bad[:5], actual[bad[:5]], expected[bad[:5]])


# ---------------------------------------------------------------------------
# The properties.
# ---------------------------------------------------------------------------


def assert_gain_invariants(households, law):
    """Properties 1, 2, 3 (no excess) and 5 for every household."""
    dividends = np.maximum(0, column(households, "dividends"))
    net_gain = np.array([net_capital_gain_after_election(h) for h in households])
    excluded = column(households, "exclusion")
    excludes = excluded > 0
    taxable_income = law["taxable_income"].astype(float)
    taxable_excess = law["amt_income_less_exemptions"].astype(float)
    cents = np.array([h["cents"] for h in households])
    scale = (
        sum(
            np.abs(column(households, key))
            for key in [
                "long_term",
                "short_term",
                "distributions",
                "dividends",
                "election",
                "section_1250",
                "rate_gain_28",
            ]
        )
        + np.abs(taxable_income)
        + np.abs(taxable_excess)
    )
    # Whole-dollar amounts below 2**24 are exact in single precision, and so
    # is every sum and difference of them the model forms. The gains and
    # worksheet lines 6 to 10 do not depend on taxable income; the section
    # 911 amounts are exact only when taxable income (or Form 6251 line 6) is
    # a whole-dollar amount too.
    exact_gains = ~cents & (scale < 2**24)
    exact = exact_gains & (taxable_income == np.round(taxable_income))
    exact_amt = exact_gains & (taxable_excess == np.round(taxable_excess))

    def check(variable, expected, mask=exact):
        assert_close(law[variable], expected, mask, scale, variable)

    # Stored in single precision, like every input.
    assert np.array_equal(
        law["foreign_earned_income_exclusion"], excluded.astype(np.float32)
    )

    # 5. The worksheet transcription, and dwks10 against net capital gain.
    lines = np.array([schedule_d_tax_worksheet(h) for h in households], dtype=float)
    assert_close(lines[:, 2], net_gain, exact_gains, scale, "closed form")
    check("dividend_income_reduced_by_investment_income", lines[:, 0], exact_gains)
    check("dwks09", lines[:, 1], exact_gains)
    check("dwks10", lines[:, 2], exact_gains)
    assert_close(law["dwks10"], law["net_capital_gain"], exact_gains, scale, "dwks10")

    # 1. Closed forms.
    check("net_capital_gain", net_gain, exact_gains)
    check(
        "dividend_income_reduced_by_investment_income",
        np.minimum(dividends, net_gain),
        exact_gains,
    )
    floor_income = np.maximum(0, taxable_income)
    check(
        "section_911_capital_gain_excess",
        np.where(excludes, np.maximum(0, net_gain - taxable_income), 0),
    )
    check(
        "section_911_net_capital_gain",
        np.where(excludes, np.minimum(net_gain, floor_income), net_gain),
    )
    check(
        "section_911_qualified_dividend_income",
        np.where(
            excludes,
            np.minimum(np.minimum(dividends, net_gain), floor_income),
            np.minimum(dividends, net_gain),
        ),
    )
    # Without an excess: qualified dividends after the election are the
    # smaller of the dividends and net capital gain, bit for bit. The tax
    # unit's dividends are summed in double precision, as the model sums
    # them, and the result is stored in single precision.
    no_excess = law["section_911_capital_gain_excess"] == 0
    after_election = np.minimum(
        np.maximum(0, law["qualified_dividends"]),
        law["net_capital_gain"],
    ).astype(np.float32)
    assert np.array_equal(
        law["section_911_qualified_dividend_income"][no_excess],
        after_election[no_excess],
    )
    # Section 911(f)(2)(A)(i)-(ii): the gain other than dividends and the
    # dividends that remain make up the reduced net capital gain.
    assert_close(
        law["gain_other_than_dividends"] + law["section_911_qualified_dividend_income"],
        law["section_911_net_capital_gain"],
        exact,
        scale,
        "reduced gain plus dividends",
    )

    # 2. The worksheet route equals the section 1(h) route.
    for line, variable in [
        ("capital_gain_excess", "section_911_capital_gain_excess"),
        ("line_10", "section_911_net_capital_gain"),
        ("line_13", "section_911_adjusted_net_capital_gain"),
        (
            "unrecaptured_section_1250_gain",
            "section_911_unrecaptured_section_1250_gain",
        ),
    ]:
        assert_close(
            law[f"worksheet_{line}"], law[variable], exact, scale, (line, variable)
        )
    assert_close(
        law["worksheet_line_9"],
        law["gain_other_than_dividends"],
        exact,
        scale,
        "line_9",
    )
    assert_close(
        law["worksheet_line_10"] - law["worksheet_line_9"],
        law["section_911_qualified_dividend_income"],
        exact,
        scale,
        "line_10 - line_9",
    )
    # Modifications 1 and 2 of the Foreign Earned Income Tax Worksheet
    # footnote, on the transcribed worksheet.
    reduced = np.array(
        [
            reduce_by_capital_gain_excess(
                max(0, line_10 - max(0, income)) if x > 0 else 0, line_6, line_9
            )
            for (line_6, line_9, line_10), income, x in zip(
                lines, taxable_income, excluded
            )
        ]
    )
    assert_close(
        law["worksheet_line_10"] - law["worksheet_line_9"],
        reduced[:, 0],
        exact,
        scale,
        "modification 2",
    )
    assert_close(law["worksheet_line_9"], reduced[:, 1], exact, scale, "modification 1")
    # The AMT excess is measured from Form 6251 line 6. It has one route
    # (amt_section_911_capital_gain_excess is the worksheet helper's excess),
    # so it is checked against its closed form.
    floor_excess = np.maximum(0, taxable_excess)
    assert_close(
        law["amt_section_911_capital_gain_excess"],
        np.where(excludes, np.maximum(0, net_gain - floor_excess), 0),
        exact_amt,
        scale,
        "amt_section_911_capital_gain_excess",
    )
    assert_close(
        law["amt_worksheet_line_10"],
        np.where(excludes, np.minimum(net_gain, floor_excess), net_gain),
        exact_amt,
        scale,
        "amt line_10",
    )

    # 3. Without an excess, each amount that section 911(f) replaces equals
    # its original, bit for bit; without an exclusion so do the stacked bases.
    # The worksheet measures its own excess, from line 10 (with cents the two
    # measures can differ by rounding).
    no_worksheet_excess = law["worksheet_capital_gain_excess"] == 0
    for variable, original, mask in [
        ("section_911_net_capital_gain", "net_capital_gain", no_excess),
        (
            "section_911_adjusted_net_capital_gain",
            "adjusted_net_capital_gain",
            no_excess,
        ),
        (
            "section_911_28_percent_rate_gain",
            "capital_gains_28_percent_rate_gain",
            no_excess,
        ),
        (
            "section_911_unrecaptured_section_1250_gain",
            "unrecaptured_section_1250_gain",
            no_excess,
        ),
        ("worksheet_line_9", "dwks09", no_worksheet_excess),
        ("worksheet_line_10", "dwks10", no_worksheet_excess),
        ("worksheet_line_13", "dwks13", no_worksheet_excess),
        (
            "worksheet_unrecaptured_section_1250_gain",
            "unrecaptured_section_1250_gain",
            no_worksheet_excess,
        ),
    ]:
        assert np.array_equal(law[variable][mask], law[original][mask]), variable
    for stacked, original in [
        ("taxable_income_plus_section_911_exclusion", "taxable_income"),
        (
            "amt_income_less_exemptions_plus_section_911_exclusion",
            "amt_income_less_exemptions",
        ),
    ]:
        assert np.array_equal(law[stacked][~excludes], law[original][~excludes])
    for variable in [
        "section_911_capital_gain_excess",
        "amt_section_911_capital_gain_excess",
    ]:
        assert not law[variable][~excludes].any(), variable


def plain(households):
    """Households inside the scope of the tax comparisons (see the module
    docstring): no 28-percent rate or unrecaptured section 1250 gain."""
    return (column(households, "section_1250") == 0) & (
        column(households, "rate_gain_28") == 0
    )


def assert_matches_2025_forms(households, law):
    """Property 6: the model against the transcribed 2025 forms."""
    for i, h in enumerate(households):
        if h["section_1250"] or h["rate_gain_28"]:
            continue
        status = law["filing_status"][i]
        assert status == h["status"], (i, status)
        taxable_income = float(law["taxable_income"][i])
        # Schedule D Tax Worksheet lines 6 and 9 take the place of lines 2
        # and 3 of the Qualified Dividends and Capital Gain Tax Worksheet.
        line_6, line_9, _ = schedule_d_tax_worksheet(h)
        line_6_feitw, line_6_capped, ordinary_income = (
            foreign_earned_income_tax_worksheet(
                taxable_income, h["exclusion"], line_6, line_9, status
            )
        )
        stacked_income = taxable_income + h["exclusion"]
        slack = tolerance(stacked_income)
        regular_tax = float(law["regular_tax"][i])
        assert regular_tax == pytest.approx(line_6_feitw, abs=slack), (i, h)
        # The line 47 cap, which the model's section 1(h) formulas omit,
        # binds by at most the rate overlap.
        cap_gap = regular_tax - line_6_capped
        assert -slack <= cap_gap <= law["rate_overlap"][i] + slack, (i, h)
        gain = section_1222_gain(h)
        if status == "SEPARATE" and h["dividends"] + gain > 0:
            # Form 6251 line 18 (see the module docstring).
            continue
        taxable_excess = float(law["amt_income_less_exemptions"][i])
        line_7 = form_6251_line_7(
            taxable_excess,
            h["exclusion"],
            line_6,
            line_9,
            ordinary_income,
            status,
        )
        amt = max(0, line_7 - line_6_feitw)
        assert float(law["alternative_minimum_tax"][i]) == pytest.approx(
            amt, abs=tolerance(stacked_income, taxable_excess)
        ), (i, h)


VARIANTS = ["law", "more_elected", "more_excluded", "unstacked", "no_election"]


def with_variants(households):
    """The households, then each one with more elected, more excluded,
    nothing excluded and nothing elected, in one batch."""
    return (
        households
        + [{**h, "election": h["election"] + h["more_elected"]} for h in households]
        + [{**h, "exclusion": 1.5 * h["exclusion"] + 500} for h in households]
        + [{**h, "exclusion": 0} for h in households]
        + [{**h, "election": 0} for h in households]
    )


def split_variants(results, count):
    return {
        name: {v: values[k * count : (k + 1) * count] for v, values in results.items()}
        for k, name in enumerate(VARIANTS)
    }


def assert_monotone(households, groups):
    """Property 4.

    For these households, the election reaches taxable income only through
    the choice to itemize. The exclusion can also reduce the SALT deduction:
    section 164(b)(7)(B)(iv) adds section 911 income back to SALT MAGI (2025
    Schedule A instructions, page 7, worksheet lines 3b and 3c).
    The model itemizes when that gives the lower
    income_tax (tax_unit_itemizes), and an AMT filer can lower the tax by
    itemizing deductions smaller than the standard deduction, which reduce
    alternative minimum taxable income. An election or exclusion that raises
    the regular tax can then change the choice. So amounts that depend on
    taxable income are compared only between variants that make the same
    choice. income_tax, the amount the choice minimizes, is compared across
    a change of choice, for households without dependents. For them no
    credit but the EITC applies; neither the EITC nor the net investment
    income tax depends on the election or the choice, and as the exclusion
    rises the EITC never rises and the net investment income tax never
    falls.
    """
    law = groups["law"]
    taxable_income = law["taxable_income"]
    itemizes = law["tax_unit_itemizes"]
    for name in VARIANTS:
        same = groups[name]["tax_unit_itemizes"] == itemizes
        if name in ("more_excluded", "unstacked"):
            same &= ~itemizes | (
                groups[name]["itemized_taxable_income_deductions"]
                == law["itemized_taxable_income_deductions"]
            )
        assert np.array_equal(
            groups[name]["taxable_income"][same], taxable_income[same]
        ), name

    more = column(households, "more_elected")
    scale = (
        np.abs(column(households, "long_term"))
        + np.abs(column(households, "short_term"))
        + column(households, "distributions")
        + column(households, "dividends")
        + column(households, "election")
        + more
        + np.abs(taxable_income)
    )
    slack = rounding(scale)
    election_pairs = [
        (groups["no_election"], law),
        (law, groups["more_elected"]),
    ]
    exclusion_pairs = [
        (groups["unstacked"], law),
        (law, groups["more_excluded"]),
    ]

    def same_choice(lower, higher):
        return lower["tax_unit_itemizes"] == higher["tax_unit_itemizes"]

    # More excluded cannot lower taxable income while the itemization
    # choice holds, including when the SALT MAGI add-back reduces deductions.
    for lower, higher in exclusion_pairs:
        rows = same_choice(lower, higher)
        assert (higher["taxable_income"] >= lower["taxable_income"])[rows].all()

    # More elected: the gains never rise, net capital gain falls by at most
    # the extra amount elected, and amounts limited by taxable income or
    # Form 6251 line 6 never rise while the choice to itemize holds.
    for variable, depends_on_income in [
        ("net_capital_gain", False),
        ("dwks10", False),
        ("section_911_net_capital_gain", True),
        ("section_911_qualified_dividend_income", True),
        ("section_911_capital_gain_excess", True),
        ("amt_section_911_capital_gain_excess", True),
    ]:
        for lower, higher in election_pairs:
            rise = higher[variable] - lower[variable]
            rows = same_choice(lower, higher) | (not depends_on_income)
            assert (rise <= slack)[rows].all(), variable
    fall = law["net_capital_gain"] - groups["more_elected"]["net_capital_gain"]
    assert (fall <= more + slack).all()

    inside = plain(households)
    excluded = np.maximum(
        column(households, "exclusion"),
        groups["more_excluded"]["foreign_earned_income_exclusion"],
    )
    tax_slack = tolerance(
        taxable_income + excluded,
        groups["more_excluded"][
            "amt_income_less_exemptions_plus_section_911_exclusion"
        ],
    )
    overlap = law["rate_overlap"]
    no_dependents = np.array([h["status"] != "HEAD_OF_HOUSEHOLD" for h in households])
    for v in ["regular_tax", "income_tax_before_credits", "income_tax"]:
        # tax_unit_itemizes treats liabilities within $0.01 as equal.
        margin = tax_slack + (0.01 if v == "income_tax" else 0)
        if v != "income_tax":
            assert (law[v] >= 0).all(), v

        def rows(lower, higher):
            if v == "income_tax":
                return inside & no_dependents
            return inside & same_choice(lower, higher)

        # More elected: the tax falls by at most the rate overlap.
        for lower, higher in election_pairs:
            dip = lower[v] - higher[v]
            mask = rows(lower, higher)
            assert (dip[mask] <= (overlap + margin)[mask]).all(), v
        # Stacking never lowers the tax, and the tax never falls as the
        # excluded amount rises.
        for lower, higher in exclusion_pairs:
            dip = lower[v] - higher[v]
            mask = rows(lower, higher)
            assert (dip[mask] <= margin[mask]).all(), v
    # Section 911(f)(1)(A) applies "if such taxpayer has taxable income".
    for name in VARIANTS:
        no_income = inside & (groups[name]["taxable_income"] == 0)
        assert not groups[name]["regular_tax"][no_income].any(), name


def assert_all(households, year, forms=False):
    count = len(households)
    batch = with_variants(households)
    results = calculate(batch, year)
    assert_gain_invariants(batch, results)
    groups = split_variants(results, count)
    assert_monotone(households, groups)
    if forms:
        assert_matches_2025_forms(batch, results)
    return groups


# ---------------------------------------------------------------------------
# A grid that reaches every branch, and generated households.
# ---------------------------------------------------------------------------


def household(**amounts):
    h = {
        "status": "SINGLE",
        "wages": 0,
        "dividends": 0,
        "long_term": 0,
        "short_term": 0,
        "distributions": 0,
        "election": 0,
        "more_elected": 1_000,
        "exclusion": 0,
        "real_estate_taxes": 0,
        "mortgage_interest": 0,
        "charitable_gifts": 0,
        "section_1250": 0,
        "rate_gain_28": 0,
        "cents": False,
    }
    h.update(amounts)
    return h


# Wages, dividends, long-term gain, short-term gain, distributions.
GRID_INCOMES = [
    (60_000, 10_000, 50_000, 0, 0),
    (0, 8_000, 30_000, -5_000, 2_000),
    (0, 40_000, 0, 0, 0),
    (700_000, 25_000, 900_000, 0, 0),
    # Gains in the AMT exemption phase-out, where the AMT exceeds the regular
    # tax.
    (20_000, 25_000, 900_000, 0, 0),
    (0, 0, -8_000, 5_000, 0),
    (20_000, 5_000, 15_000, 3_000, 1_000),
]


def grid():
    rows = []
    for status in STATUSES:
        for wages, dividends, long_term, short_term, distributions in GRID_INCOMES:
            base = household(
                status=status,
                wages=wages,
                dividends=dividends,
                long_term=long_term,
                short_term=short_term,
                distributions=distributions,
            )
            gain = section_1222_gain(base)
            for election in sorted(
                {0, 2_000, gain, gain + dividends // 2, gain + dividends + 50_000}
            ):
                for exclusion in (0, 40_025, 260_000):
                    rows.append({**base, "election": election, "exclusion": exclusion})
    # Itemizers, and 28-percent rate and unrecaptured section 1250 gain.
    rows += [
        {
            **row,
            "real_estate_taxes": 12_000,
            "charitable_gifts": 40_000,
            "section_1250": 15_000,
            "rate_gain_28": 10_000,
        }
        for row in rows[::7]
    ]
    return rows


# 2025 Schedule A instructions, page 7, State and Local Tax Deduction
# Worksheet lines 2 to 10: AGI of $480,000 plus $100,000 from Form 2555
# raises MAGI to $580,000. The $40,000 SALT cap falls by 30% of $80,000
# to $16,000. Both returns itemize, but taxable income rises by $24,000.
# https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=7
SALT_PHASE_OUT_CASES = [
    household(
        wages=450_000,
        long_term=30_000,
        election=10_000,
        real_estate_taxes=60_000,
        exclusion=x,
    )
    for x in (0, 100_000)
]

GRID = grid() + SALT_PHASE_OUT_CASES


def test_grid():
    groups = assert_all(GRID, 2025, forms=True)
    law = groups["law"]
    elects = column(GRID, "election") > 0
    excludes = column(GRID, "exclusion") > 0
    both = elects & excludes
    excess = law["section_911_capital_gain_excess"]
    # The grid reaches each part of the interaction: an election with and
    # without a capital gain excess, an excess that reaches the dividends the
    # election leaves, an election that reaches the dividends, the AMT, the
    # capital gains tax and no taxable income.
    assert (both & (excess > 0)).any()
    assert (both & (excess == 0)).any()
    assert (both & (excess > law["dwks09"]) & (law["dwks09"] > 0)).any()
    reached_dividends = law["dividend_income_reduced_by_investment_income"] < (
        column(GRID, "dividends")
    )
    assert (both & reached_dividends & (excess > 0)).any()
    assert (both & (law["alternative_minimum_tax"] > 0)).any()
    assert (both & (law["capital_gains_tax"] > 0)).any()
    assert (both & (law["taxable_income"] == 0)).any()
    assert (both & (law["amt_section_911_capital_gain_excess"] > 0)).any()
    # Electing more and stacking each raise the tax of some households.
    assert (groups["more_elected"]["regular_tax"] > law["regular_tax"] + 1).any()
    assert (law["regular_tax"] > groups["unstacked"]["regular_tax"] + 1).any()

    # The SALT cases also exercise the variants and independent form
    # comparisons above, reusing the grid's simulation.
    salt = {v: values[-len(SALT_PHASE_OUT_CASES) :] for v, values in law.items()}
    assert salt["tax_unit_itemizes"].all()
    assert salt["agi_plus_section_911_931_933_exclusions"] == pytest.approx(
        [480_000, 580_000]
    )
    assert salt["salt_cap"] == pytest.approx([40_000, 16_000])
    assert salt["salt_deduction"] == pytest.approx([40_000, 16_000])
    assert salt["taxable_income"] == pytest.approx([440_000, 464_000])


def test_election_can_lower_the_tax_where_15_percent_exceeds_12():
    """An intended exception to "electing more never lowers the tax".

    2025, single, no other income than wages and a $10,000 long-term gain.
    Without an exclusion, $64,100 of wages and the gain, less the $15,750
    standard deduction, leave $58,350 of taxable income, $48,350 of it
    ordinary: the gain starts at the 15% rate, inside the 12% bracket, which
    ends at $48,475. With $55,750 of wages, taxable income is $50,000, and
    with $8,350 excluded worksheet line 3 is the same $58,350 (no capital gain
    excess, since the gain is below taxable income). Electing $125 taxes $125 more at 12%
    ($15) and $125 less at 15% ($18.75): the tax falls by $3.75. The
    Schedule D Tax Worksheet with its line 47 cap falls by the same amount.
    """
    households = [
        household(wages=wages, long_term=10_000, election=election, exclusion=x)
        for wages, x in [(64_100, 0), (55_750, 8_350)]
        for election in (0, 125)
    ]
    law = calculate(households, 2025)
    assert (law["taxable_income"] + column(households, "exclusion") == 58_350).all()
    assert list(law["rate_overlap"]) == pytest.approx([3.75] * 4)
    regular_tax = law["regular_tax"].reshape(2, 2)
    assert list(regular_tax[:, 1] - regular_tax[:, 0]) == pytest.approx([-3.75] * 2)
    assert np.array_equal(law["income_tax_before_credits"].reshape(2, 2), regular_tax)
    on_the_form = np.array(
        [
            foreign_earned_income_tax_worksheet(
                float(law["taxable_income"][i]),
                h["exclusion"],
                *schedule_d_tax_worksheet(h)[:2],
                "SINGLE",
            )[1]
            for i, h in enumerate(households)
        ]
    ).reshape(2, 2)
    assert list(on_the_form[:, 1] - on_the_form[:, 0]) == pytest.approx([-3.75] * 2)
    # Without the exclusion the form's tax is the worksheet's line 47.
    _, _, line_47 = qualified_dividends_and_capital_gain_tax_worksheet(
        58_350, 0, 10_000, "SINGLE"
    )
    assert on_the_form[0, 0] == pytest.approx(line_47)
    assert line_47 < tax_rate_schedule(58_350, "SINGLE")


@st.composite
def households(draw):
    h = household(
        status=draw(st.sampled_from(STATUSES)),
        wages=draw(st.one_of(st.just(0), st.integers(1, 900_000))),
        dividends=draw(st.one_of(st.just(0), st.integers(1, 300_000))),
        long_term=draw(st.one_of(st.just(0), st.integers(-50_000, 1_500_000))),
        short_term=draw(st.one_of(st.just(0), st.integers(-100_000, 100_000))),
        distributions=draw(st.one_of(st.just(0), st.integers(1, 100_000))),
        exclusion=draw(st.one_of(st.just(0), st.integers(1, 300_000))),
        real_estate_taxes=draw(st.one_of(st.just(0), st.integers(1, 60_000))),
        mortgage_interest=draw(st.one_of(st.just(0), st.integers(1, 80_000))),
        charitable_gifts=draw(st.one_of(st.just(0), st.integers(1, 150_000))),
        more_elected=draw(st.one_of(st.integers(1, 500), st.integers(1, 500_000))),
    )
    gain = section_1222_gain(h)
    # Elections at the gain and at the gain plus dividends are where the
    # election starts and stops reducing qualified dividends.
    h["election"] = draw(
        st.one_of(
            st.just(0),
            st.integers(1, 2_000_000),
            st.sampled_from([gain, gain + h["dividends"]]),
            st.integers(max(0, gain - 5), gain + h["dividends"] + 5),
        )
    )
    if draw(st.integers(0, 3)) == 0:
        h["section_1250"] = draw(st.integers(0, 200_000))
        h["rate_gain_28"] = draw(st.integers(0, 200_000))
    if draw(st.integers(0, 3)) == 0:
        # Amounts with cents, which single precision cannot store exactly.
        for key in [
            "dividends",
            "long_term",
            "short_term",
            "distributions",
            "election",
            "exclusion",
        ]:
            if h[key]:
                h[key] = h[key] + draw(st.integers(1, 99)) / 100
        h["cents"] = True
    return h


SETTINGS = dict(
    deadline=None,
    derandomize=True,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)


@hypothesis.settings(max_examples=10, **SETTINGS)
@hypothesis.given(
    st.lists(households(), min_size=1, max_size=20), st.sampled_from(YEARS)
)
def test_random_households_keep_the_invariants(batch, year):
    assert_all(batch, year)


@hypothesis.settings(max_examples=10, **SETTINGS)
@hypothesis.given(st.lists(households(), min_size=1, max_size=20))
# Found by this test. Without the election the filer is in the AMT and
# itemizes $1,915 (Texas sales tax and a $1 gift), less than the standard
# deduction, which lowers alternative minimum taxable income; electing $1,917
# raises the regular tax above the tentative minimum tax, the filer takes the
# standard deduction, and taxable income falls by $13,835.
@hypothesis.example(
    [household(long_term=971_091, election=1_917, more_elected=1, charitable_gifts=1)]
)
# Dividends with cents split between spouses: the model sums them in double
# precision and stores the result in single precision.
@hypothesis.example(
    [
        household(
            status="JOINT",
            dividends=2_554.33,
            long_term=30_000.57,
            election=1_000.01,
            exclusion=60_000.25,
            cents=True,
        )
    ]
)
def test_random_households_match_the_2025_forms(batch):
    assert_all(batch, 2025, forms=True)


@hypothesis.settings(max_examples=6, **SETTINGS)
@hypothesis.given(
    st.lists(households(), min_size=2, max_size=20), st.sampled_from(YEARS)
)
def test_zero_election_or_exclusion_matches_the_situation_without_it(batch, year):
    """Property 3: a household that elects nothing gets the results of the
    situation test_section_911_tax_stacking.py builds (no election input),
    and one that excludes nothing those of the situation
    test_form_4952_election_worksheet.py builds (no exclusion input), bit for
    bit, whatever its neighbours in the batch elect or exclude.

    Both amounts are inputs without formulas, so a zero input equals no
    input by construction; what this checks is that no household's election
    or exclusion reaches another household's results. Property 1 checks the
    no-election and no-exclusion paths themselves."""
    both = calculate(batch, year)
    no_election = calculate(batch, year, with_election=False)
    no_exclusion = calculate(batch, year, with_exclusion=False)
    elects = column(batch, "election") > 0
    excludes = column(batch, "exclusion") > 0
    for v in OUTPUTS + ["regular_tax", "gain_other_than_dividends"]:
        assert np.array_equal(both[v][~elects], no_election[v][~elects]), v
        assert np.array_equal(both[v][~excludes], no_exclusion[v][~excludes]), v
