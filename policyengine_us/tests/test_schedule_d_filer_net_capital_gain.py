"""Property tests: the tax on net capital gain uses the filers' Schedule D.

26 U.S.C. 1(h) taxes a net capital gain at lower rates. Net capital gain is
the net long-term capital gain over the net short-term capital loss (26 U.S.C.
1222(11)), plus qualified dividend income (1(h)(11)(A)). On the return these
are Schedule D lines 15 and 16 (2025 Schedule D) and Form 1040 line 3a, and
the Schedule D Tax Worksheet starts from "the smaller of line 15 or line 16"
(2025 Instructions for Schedule D, page 15). Capital gain distributions
reported without Schedule D go on line 13, inside line 15 (2025 Instructions
for Schedule D, "Capital Gain Distributions"). Form 1099-DIV box 2a reports
them, so they are never negative.

A tax unit dependent's gains, losses and dividends are on the dependent's own
return (2025 Form 8814, line 4), and adjusted gross income leaves them out.
So for every combination of the filers' long-term (LT) and short-term (ST)
gains and losses, distributions (D) and qualified dividends (Q), and anything
the tax unit's dependents have:

1. net_capital_gain = max(0, min(line 15, line 16)) + Q, where line 15 is
   LT + max(0, D) and line 16 is line 15 + ST, over the head and spouse.
2. The Schedule D Tax Worksheet agrees: line 9 (dwks09) is
   max(0, min(line 15, line 16)), line 6 is Q, and line 10 (dwks10) equals
   net_capital_gain, which figures the same amount from 1222(11). This is a
   differential check between the two paths.
3. has_qdiv_or_ltcg is true exactly when Q > 0 or lines 15 and 16 are both
   more than zero (Form 1040 line 16 instructions).
4. Form 1040 line 7a (filer_loss_limited_net_capital_gains) is line 16, or
   the loss limit if line 16 is a larger loss, from the same lines.
5. Changing a dependent's capital gains, losses, distributions, dividends,
   collectibles and section 1202 gain, long-term loss carryover, Schedule D
   line 18 amounts or Form 4952 election changes none of the filers' tax
   amounts.
6. A negative distributions input gives the same results as zero.
7. Net capital gain never falls when a filer's LT, ST, D or Q rises, and
   rises by no more than the increase.

Amounts are whole dollars of at most $1,000,000, so every sum is exact in
single precision and the comparisons are exact.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025

FILER_INPUTS = {
    "long_term": "long_term_capital_gains",
    "short_term": "short_term_capital_gains",
    "distributions": "non_sch_d_capital_gains",
    "dividends": "qualified_dividend_income",
}
DEPENDENT_INPUTS = {
    **FILER_INPUTS,
    "collectibles": "collectibles_gain_or_loss",
    "line_18_collectibles": "long_term_capital_gains_on_collectibles",
    "line_18_small_business_stock": "long_term_capital_gains_on_small_business_stock",
    "section_1202": "section_1202_gain",
    "carryover": "long_term_capital_loss_carryover",
    "election": "investment_income_elected_form_4952",
}

# The head and spouse's amounts, which must not depend on a dependent's.
TAX_OUTPUTS = [
    "net_capital_gain",
    "adjusted_net_capital_gain",
    "dwks09",
    "dwks10",
    "dividend_income_reduced_by_investment_income",
    "has_qdiv_or_ltcg",
    "capital_gains_28_percent_rate_gain",
    "schedule_d_unrecaptured_section_1250_gain",
    "filer_loss_limited_net_capital_gains",
    "adjusted_gross_income",
    "taxable_income",
    "capital_gains_tax",
    "income_tax_main_rates",
    "alternative_minimum_tax",
    "income_tax_before_credits",
]


def schedule_d_lines(h):
    """Schedule D lines 15 and 16 and Form 1040 line 3a of the filers."""
    filers = h["filers"]
    line_15 = sum(p["long_term"] + max(0, p["distributions"]) for p in filers)
    line_16 = line_15 + sum(p["short_term"] for p in filers)
    dividends = sum(p["dividends"] for p in filers)
    return line_15, line_16, dividends


def build_situation(households):
    """One tax unit per household: a head, an optional spouse and any
    dependents, each dependent in a marital unit of their own."""
    people, tax_units, marital_units, households_out = {}, {}, {}, {}
    for i, h in enumerate(households):
        filers, members = [], []
        for j, p in enumerate(h["filers"]):
            name = f"filer_{i}_{j}"
            people[name] = {
                "age": {YEAR: 45},
                "is_tax_unit_head": {YEAR: j == 0},
                "is_tax_unit_spouse": {YEAR: j == 1},
                "is_tax_unit_dependent": {YEAR: False},
                "employment_income": {YEAR: h["wages"] if j == 0 else 0},
                **{v: {YEAR: p[k]} for k, v in FILER_INPUTS.items()},
            }
            filers.append(name)
        for j, p in enumerate(h["dependents"]):
            name = f"dependent_{i}_{j}"
            people[name] = {
                "age": {YEAR: 10},
                "is_tax_unit_head": {YEAR: False},
                "is_tax_unit_spouse": {YEAR: False},
                "is_tax_unit_dependent": {YEAR: True},
                "employment_income": {YEAR: 0},
                **{v: {YEAR: p.get(k, 0)} for k, v in DEPENDENT_INPUTS.items()},
            }
            marital_units[f"dependent_marital_unit_{i}_{j}"] = {"members": [name]}
            members.append(name)
        members = filers + members
        tax_units[f"tax_unit_{i}"] = {"members": members}
        marital_units[f"marital_unit_{i}"] = {"members": filers}
        households_out[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households_out,
    }


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    results = {v: np.asarray(simulation.calculate(v, YEAR)) for v in TAX_OUTPUTS}
    results["filing_status"] = np.asarray(
        simulation.calculate("filing_status", YEAR).decode_to_str()
    )
    return results


def assert_properties(households):
    model = calculate(households)
    for i, h in enumerate(households):
        line_15, line_16, dividends = schedule_d_lines(h)
        gain = max(0, min(line_15, line_16))
        # 1. 26 U.S.C. 1222(11) and 1(h)(11)(A) on the filers' return.
        assert model["net_capital_gain"][i] == gain + dividends, h
        # 2. The Schedule D Tax Worksheet, lines 6, 9 and 10.
        assert model["dividend_income_reduced_by_investment_income"][i] == (
            dividends
        ), h
        assert model["dwks09"][i] == gain, h
        assert model["dwks10"][i] == model["net_capital_gain"][i], h
        # 3. Form 1040 line 16 routing.
        assert bool(model["has_qdiv_or_ltcg"][i]) == (
            dividends > 0 or (line_15 > 0 and line_16 > 0)
        ), h
        # 4. Form 1040 line 7a, Schedule D line 16 or line 21.
        limit = 1_500 if model["filing_status"][i] == "SEPARATE" else 3_000
        assert model["filer_loss_limited_net_capital_gains"][i] == max(
            -limit, line_16
        ), h
        # No collectibles, section 1202 or section 1250 gain on the return.
        assert model["adjusted_net_capital_gain"][i] == model["net_capital_gain"][i], h


def without_dependents_amounts(households):
    return [{**h, "dependents": [{} for _ in h["dependents"]]} for h in households]


def assert_dependents_change_nothing(households):
    """5. The filers' amounts with the dependents' inputs and without them."""
    with_amounts = calculate(households)
    without_amounts = calculate(without_dependents_amounts(households))
    for variable in TAX_OUTPUTS:
        assert np.array_equal(with_amounts[variable], without_amounts[variable]), (
            variable,
            households,
        )


# ---------------------------------------------------------------------------
# A deterministic grid.
# ---------------------------------------------------------------------------

GRID_GAINS = [-12_000, -3_000, 0, 4_000, 25_000]
GRID_DISTRIBUTIONS = [-2_000, 0, 3_000]
GRID_DEPENDENT = {
    "long_term": 20_000,
    "short_term": -8_000,
    "distributions": 1_000,
    "dividends": 5_000,
    "collectibles": 4_000,
    "line_18_collectibles": 2_000,
    "line_18_small_business_stock": 1_000,
    "section_1202": 3_000,
    "carryover": 2_000,
    "election": 3_000,
}


def grid_households():
    households = []
    for lt, st_, d, q in itertools.product(
        GRID_GAINS, GRID_GAINS, GRID_DISTRIBUTIONS, [0, 2_000]
    ):
        filer = {"long_term": lt, "short_term": st_, "distributions": d, "dividends": q}
        none = {"long_term": 0, "short_term": 0, "distributions": 0, "dividends": 0}
        households.append(
            {"wages": 60_000, "filers": [filer], "dependents": [GRID_DEPENDENT]}
        )
        # The same totals split between spouses, with two dependents.
        households.append(
            {
                "wages": 150_000,
                "filers": [
                    {**none, "long_term": lt, "distributions": d},
                    {**none, "short_term": st_, "dividends": q},
                ],
                "dependents": [GRID_DEPENDENT, {"long_term": -5_000}],
            }
        )
    return households


def test_grid():
    households = grid_households()
    assert_properties(households)
    assert_dependents_change_nothing(households)


def test_reported_case():
    """A single filer with wages 60,000 and a 10,000 long-term gain, and a
    dependent child with a 20,000 long-term gain: the child's gain is on the
    child's own return, so net capital gain is 10,000, not 30,000."""
    h = {
        "wages": 60_000,
        "filers": [
            {"long_term": 10_000, "short_term": 0, "distributions": 0, "dividends": 0}
        ],
        "dependents": [{"long_term": 20_000}],
    }
    model = calculate([h])
    assert model["net_capital_gain"][0] == 10_000
    assert model["dwks10"][0] == 10_000
    assert model["adjusted_gross_income"][0] == 70_000


# ---------------------------------------------------------------------------
# Hypothesis.
# ---------------------------------------------------------------------------

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

AMOUNT = st.integers(min_value=-1_000_000, max_value=1_000_000)
SMALL = st.integers(min_value=-20_000, max_value=20_000)
NON_NEGATIVE = st.one_of(
    st.just(0),
    st.integers(min_value=0, max_value=20_000),
    st.integers(min_value=0, max_value=1_000_000),
)
# Distributions inputs, including negative ones, which count as zero.
DISTRIBUTIONS = st.one_of(NON_NEGATIVE, st.integers(min_value=-50_000, max_value=-1))
WAGES = st.sampled_from([0, 40_000, 150_000, 600_000])


@st.composite
def filer(draw):
    amounts = draw(st.sampled_from([AMOUNT, SMALL]))
    return {
        "long_term": draw(st.one_of(st.just(0), amounts)),
        "short_term": draw(st.one_of(st.just(0), amounts)),
        "distributions": draw(DISTRIBUTIONS),
        "dividends": draw(NON_NEGATIVE),
    }


@st.composite
def dependent(draw):
    return {
        "long_term": draw(st.one_of(st.just(0), SMALL, AMOUNT)),
        "short_term": draw(st.one_of(st.just(0), SMALL, AMOUNT)),
        "distributions": draw(DISTRIBUTIONS),
        "dividends": draw(NON_NEGATIVE),
        "collectibles": draw(st.one_of(st.just(0), SMALL)),
        "line_18_collectibles": draw(st.one_of(st.just(0), NON_NEGATIVE)),
        "line_18_small_business_stock": draw(st.one_of(st.just(0), NON_NEGATIVE)),
        "section_1202": draw(st.one_of(st.just(0), NON_NEGATIVE)),
        "carryover": draw(st.one_of(st.just(0), NON_NEGATIVE)),
        "election": draw(st.one_of(st.just(0), NON_NEGATIVE)),
    }


@st.composite
def household(draw):
    return {
        "wages": draw(WAGES),
        "filers": [draw(filer()) for _ in range(draw(st.integers(1, 2)))],
        "dependents": [draw(dependent()) for _ in range(draw(st.integers(0, 2)))],
    }


@hypothesis.settings(max_examples=30, deadline=None)
@hypothesis.given(st.lists(household(), min_size=1, max_size=8))
def test_properties(households):
    assert_properties(households)


@hypothesis.settings(max_examples=20, deadline=None)
@hypothesis.given(st.lists(household(), min_size=1, max_size=8))
def test_dependents_change_nothing_on_the_filers_return(households):
    assert_dependents_change_nothing(households)


@hypothesis.settings(max_examples=20, deadline=None)
@hypothesis.given(st.lists(household(), min_size=1, max_size=8))
def test_negative_distributions_count_as_zero(households):
    """6. Flooring each filer's distributions at zero changes nothing."""
    floored = [
        {
            **h,
            "filers": [
                {**p, "distributions": max(0, p["distributions"])} for p in h["filers"]
            ],
        }
        for h in households
    ]
    model = calculate(households)
    reference = calculate(floored)
    for variable in TAX_OUTPUTS:
        assert np.array_equal(model[variable], reference[variable]), variable


@hypothesis.settings(max_examples=20, deadline=None)
@hypothesis.given(
    st.lists(household(), min_size=1, max_size=8),
    st.sampled_from(sorted(FILER_INPUTS)),
    st.integers(min_value=1, max_value=50_000),
)
def test_net_capital_gain_rises_with_the_filers_gains(households, item, extra):
    """7. Net capital gain is non-decreasing in each of the head's LT, ST,
    D (once it is not negative) and Q, and rises by at most the increase."""
    households = [
        {
            **h,
            "filers": [
                {
                    **h["filers"][0],
                    "distributions": max(0, h["filers"][0]["distributions"]),
                }
            ]
            + h["filers"][1:],
        }
        for h in households
    ]
    raised = [
        {
            **h,
            "filers": [{**h["filers"][0], item: h["filers"][0][item] + extra}]
            + h["filers"][1:],
        }
        for h in households
    ]
    base = calculate(households)["net_capital_gain"]
    more = calculate(raised)["net_capital_gain"]
    assert (more >= base).all()
    assert (more - base <= extra).all()
