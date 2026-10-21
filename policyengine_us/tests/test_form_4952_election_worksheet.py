"""Differential and property tests for the Form 4952 line 4g election.

A taxpayer may elect to treat net capital gain and qualified dividends as
investment income under 26 U.S.C. 163(d)(4)(B). The model applies the
election twice:

- `net_capital_gain` follows the statute: section 1(h)(2) removes the gain
  taken into account under section 163(d)(4)(B)(iii), and section
  1(h)(11)(D)(i) removes elected dividends from qualified dividend income.
- `dividend_income_reduced_by_investment_income`, `dwks09` and `dwks10`
  follow lines 2 to 10 of the 2025 Schedule D Tax Worksheet (Instructions
  for Schedule D, page 15).

Both attribute the election first to net capital gain and then to qualified
dividends, as the 2025 Form 4952 line 4g instructions do by default. These
tests check that the two routes, and a line-by-line transcription of the
worksheet below, agree for every combination of gains, losses, capital gain
distributions, dividends and elections.

Amounts are whole dollars of at most $2,000,000, so every sum the model forms
is below 2**24 and exact in single precision, and the comparisons are exact.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEAR = 2025

# ---------------------------------------------------------------------------
# The worksheet and Form 4952 line 4, transcribed.
# ---------------------------------------------------------------------------


def form_4952_line_4e(h):
    """2025 Form 4952 lines 4d and 4e with every capital asset held for
    investment. Line 4d: "the excess, if any, of your total gains over your
    total losses ... include capital gain distributions". Line 4e: "the
    smaller of line 4d or your net capital gain from the disposition of
    property held for investment", which is "the excess, if any, of your net
    long-term capital gain over your net short-term capital loss"; capital
    gain distributions "are treated as long-term capital gains"."""
    long_term = h["long_term"] + h["distributions"]
    line_4d = max(0, long_term + h["short_term"])
    net_capital_gain = max(0, long_term - max(0, -h["short_term"]))
    return min(line_4d, net_capital_gain)


def schedule_d_tax_worksheet(h):
    """2025 Schedule D Tax Worksheet lines 2 to 10. Returns lines 6, 9 and 10.

    Capital gain distributions go on Schedule D line 13, so they are part of
    lines 15 and 16.
    """
    schedule_d_line_15 = h["long_term"] + h["distributions"]
    schedule_d_line_16 = schedule_d_line_15 + h["short_term"]
    line_2 = h["dividends"]
    line_3 = h["election"]
    line_4 = form_4952_line_4e(h)
    line_5 = max(0, line_3 - line_4)
    line_6 = max(0, line_2 - line_5)
    line_7 = min(schedule_d_line_15, schedule_d_line_16)
    line_8 = min(line_3, line_4)
    line_9 = max(0, line_7 - line_8)
    line_10 = line_6 + line_9
    return line_6, line_9, line_10


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------

OUTPUTS = [
    "dividend_income_reduced_by_investment_income",
    "dwks09",
    "dwks10",
    "dwks13",
    "net_capital_gain",
    "adjusted_net_capital_gain",
]


def build_situation(households):
    """One single-person tax unit per household. The election and the
    dividends are split between spouses when `split` is set, to check that
    the model sums them over the tax unit."""
    people, tax_units, households_out = {}, {}, {}
    for i, h in enumerate(households):
        head = {
            "age": {YEAR: 45},
            "long_term_capital_gains": {YEAR: h["long_term"]},
            "short_term_capital_gains": {YEAR: h["short_term"]},
            "non_sch_d_capital_gains": {YEAR: h["distributions"]},
            "qualified_dividend_income": {YEAR: h["dividends"]},
            "investment_income_elected_form_4952": {YEAR: h["election"]},
        }
        members = [f"head_{i}"]
        if h["split"]:
            half_dividends = h["dividends"] // 2
            half_election = h["election"] // 2
            head["qualified_dividend_income"] = {YEAR: h["dividends"] - half_dividends}
            head["investment_income_elected_form_4952"] = {
                YEAR: h["election"] - half_election
            }
            people[f"spouse_{i}"] = {
                "age": {YEAR: 45},
                "qualified_dividend_income": {YEAR: half_dividends},
                "investment_income_elected_form_4952": {YEAR: half_election},
            }
            members.append(f"spouse_{i}")
        people[f"head_{i}"] = head
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "unrecaptured_section_1250_gain": {YEAR: h["section_1250"]},
            "capital_gains_28_percent_rate_gain": {YEAR: h["rate_gain_28"]},
        }
        households_out[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households_out}


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    return {v: np.asarray(simulation.calculate(v, YEAR)) for v in OUTPUTS}


def assert_worksheet_equals_statute(households):
    model = calculate(households)
    for i, h in enumerate(households):
        line_6, line_9, line_10 = schedule_d_tax_worksheet(h)
        assert model["dividend_income_reduced_by_investment_income"][i] == line_6, h
        assert model["dwks09"][i] == line_9, h
        assert model["dwks10"][i] == line_10, h
        # The statute route reaches worksheet line 10.
        assert model["net_capital_gain"][i] == line_10, h
        # Section 1(h)(3) against worksheet line 13: line 10 less the smaller
        # of line 9 or line 11 (Schedule D lines 18 and 19).
        line_11 = h["section_1250"] + h["rate_gain_28"]
        line_13 = line_10 - min(line_9, line_11)
        assert model["dwks13"][i] == line_13, h
        assert model["adjusted_net_capital_gain"][i] == line_13, h
        # Bounds: the election never adds gain, never removes more than it
        # elects, and never takes line 10 below zero.
        before_election = h["dividends"] + max(
            0,
            min(h["long_term"], h["long_term"] + h["short_term"]) + h["distributions"],
        )
        assert 0 <= line_10 <= before_election, h
        assert line_10 >= before_election - h["election"], h
    return model


# ---------------------------------------------------------------------------
# Strategies. Bounds keep every model sum below 2**24.
# ---------------------------------------------------------------------------

DOLLARS = 2_000_000


@st.composite
def households(draw):
    long_term = draw(
        st.one_of(
            st.just(0),
            st.integers(-DOLLARS // 4, DOLLARS),
        )
    )
    short_term = draw(st.one_of(st.just(0), st.integers(-DOLLARS // 4, DOLLARS // 4)))
    distributions = draw(st.one_of(st.just(0), st.integers(0, DOLLARS // 8)))
    dividends = draw(st.one_of(st.just(0), st.integers(0, DOLLARS)))
    gain = max(
        0, min(long_term + distributions, long_term + distributions + short_term)
    )
    # Elections near the gain and near the gain plus dividends are the
    # boundaries of the worksheet's min and max steps.
    election = draw(
        st.one_of(
            st.just(0),
            st.integers(0, DOLLARS),
            st.sampled_from([gain, gain + dividends]),
            st.integers(max(0, gain - 5), gain + dividends + 5),
        )
    )
    return {
        "long_term": long_term,
        "short_term": short_term,
        "distributions": distributions,
        "dividends": dividends,
        "election": election,
        "section_1250": draw(st.one_of(st.just(0), st.integers(0, DOLLARS // 4))),
        "rate_gain_28": draw(st.one_of(st.just(0), st.integers(0, DOLLARS // 4))),
        "split": draw(st.booleans()),
    }


GRID = [
    {
        "long_term": long_term,
        "short_term": short_term,
        "distributions": distributions,
        "dividends": dividends,
        "election": election,
        "section_1250": section_1250,
        "rate_gain_28": 0,
        "split": split,
    }
    for long_term, short_term in (
        (0, 0),
        (300_000, 0),
        (40_000, -10_000),
        (40_000, 15_000),
        (-5_000, 0),
        (5_000, -20_000),
    )
    for distributions in (0, 3_000)
    for dividends in (0, 30_000)
    for election in (0, 2_000, 35_000, 50_000, 400_000)
    for section_1250, split in ((0, False), (20_000, True))
]


def test_user_example():
    """A $50,000 election against a $300,000 long-term gain gives worksheet
    lines 9 and 10 of $250,000, and the same net capital gain."""
    h = {
        "long_term": 300_000,
        "short_term": 0,
        "distributions": 0,
        "dividends": 0,
        "election": 50_000,
        "section_1250": 0,
        "rate_gain_28": 0,
        "split": False,
    }
    assert schedule_d_tax_worksheet(h) == (0, 250_000, 250_000)
    model = assert_worksheet_equals_statute([h])
    assert model["dwks10"][0] == 250_000
    assert model["net_capital_gain"][0] == 250_000


def test_grid():
    model = assert_worksheet_equals_statute(GRID)
    # The grid reaches each branch: an election inside the gain, one that
    # spills into dividends, and one that exceeds both.
    assert (model["dwks10"] > 0).any() and (model["dwks10"] == 0).any()
    reduced = model["dividend_income_reduced_by_investment_income"]
    dividends = np.array([h["dividends"] for h in GRID])
    assert ((reduced > 0) & (reduced < dividends)).any()


@hypothesis.settings(max_examples=40, deadline=None, derandomize=True)
@hypothesis.given(st.lists(households(), min_size=1, max_size=25))
def test_worksheet_equals_statute(batch):
    assert_worksheet_equals_statute(batch)


@hypothesis.settings(max_examples=15, deadline=None, derandomize=True)
@hypothesis.given(households(), st.integers(0, DOLLARS))
def test_more_election_never_raises_line_10(h, more):
    """Line 10 is non-increasing in the election and falls by at most the
    extra amount elected."""
    larger = dict(h, election=h["election"] + more)
    model = calculate([h, larger])
    assert model["dwks10"][1] <= model["dwks10"][0]
    assert model["dwks10"][0] - model["dwks10"][1] <= more
    assert np.array_equal(model["dwks10"], model["net_capital_gain"])
