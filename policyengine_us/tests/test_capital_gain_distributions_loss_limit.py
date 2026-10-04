"""Property tests: capital gain distributions net inside the capital loss limit.

A filer with capital losses or other capital gains files Schedule D and enters
capital gain distributions on line 13 (2025 Instructions for Schedule D,
"Capital Gain Distributions"). Line 16 combines the short-term and long-term
totals, and if it is a loss, line 21 limits it to $3,000 ($1,500 married
filing separately), as 26 U.S.C. 1211(b) does. Form 1040 line 7a is line 16,
or line 21. A filer whose only capital gains are distributions skips
Schedule D and reports them on line 7a directly (Form 1040 instructions, line
7a, Exception 1); the amount is the same.

So for every combination of long-term (LT) and short-term (ST) gains and
losses and distributions (D) of the filers on a return:

1. The capital gain or loss in adjusted gross income, and
   loss_limited_net_capital_gains, equal max(-limit, LT + ST + D).
2. capital_losses_allowed_against_gains and limited_capital_loss split the
   1211(b) allowance: the losses allowed up to the gains, and the net loss,
   which is between 0 and the limit.
3. Net investment income (Form 8960 line 5a) is the same Form 1040 line 7a
   amount.
4. has_qdiv_or_ltcg is true exactly when Schedule D lines 15 (LT + D) and 16
   (LT + D + ST) are both more than zero.
5. The people's shares in loss_limited_net_capital_gains_person add up to the
   tax unit amount (to within single-precision rounding of the proportional
   split of a net loss).
6. Without Schedule D gains or losses the results are the distributions, as
   before the change.
7. A dependent's modified AGI for Social Security (IRC 86(b)(2)), figured on
   the dependent's own return, nets the same way.

Amounts are whole dollars of at most $2,000,000, so every sum is exact in
single precision and the comparisons are exact, apart from the person shares
in 5.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
LIMIT = {"SINGLE": 3_000, "JOINT": 3_000, "SEPARATE": 1_500}

OUTPUTS = [
    "adjusted_gross_income",
    "loss_limited_net_capital_gains",
    "capital_losses_allowed_against_gains",
    "limited_capital_loss",
    "net_investment_income",
    "has_qdiv_or_ltcg",
]


def line_7a(h):
    """Form 1040 line 7a from the return's totals."""
    total = sum(
        p["long_term"] + p["short_term"] + p["distributions"] for p in h["people"]
    )
    return max(-LIMIT[h["filing_status"]], total)


def schedule_d_lines_15_16(h):
    line_15 = sum(p["long_term"] + p["distributions"] for p in h["people"])
    line_16 = line_15 + sum(p["short_term"] for p in h["people"])
    return line_15, line_16


def build_situation(households):
    """One tax unit per household, with only capital gains, losses and
    distributions, so adjusted gross income is the capital gain or loss."""
    people, tax_units, marital_units, households_out = {}, {}, {}, {}
    for i, h in enumerate(households):
        members = []
        for j, p in enumerate(h["people"]):
            name = f"person_{i}_{j}"
            people[name] = {
                "age": {YEAR: 45},
                "long_term_capital_gains": {YEAR: p["long_term"]},
                "short_term_capital_gains": {YEAR: p["short_term"]},
                "non_sch_d_capital_gains": {YEAR: p["distributions"]},
            }
            members.append(name)
        # Set on every unit: a variable input for some units gives the
        # others its default value, not its formula.
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {YEAR: h["filing_status"]},
        }
        marital_units[f"marital_unit_{i}"] = {"members": members}
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
    results = {v: np.asarray(simulation.calculate(v, YEAR)) for v in OUTPUTS}
    results["filing_status"] = np.asarray(
        simulation.calculate("filing_status", YEAR).decode_to_str()
    )
    results["person_share"] = np.asarray(
        simulation.calculate("loss_limited_net_capital_gains_person", YEAR)
    )
    return results


def assert_properties(households):
    model = calculate(households)
    person = 0
    for i, h in enumerate(households):
        fs = h["filing_status"]
        assert model["filing_status"][i] == fs, h
        limit = LIMIT[fs]
        expected = line_7a(h)
        # 1. AGI and Form 1040 line 7a.
        assert model["adjusted_gross_income"][i] == expected, h
        assert model["loss_limited_net_capital_gains"][i] == expected, h
        # 2. The 1211(b) split, and the identity it gives: gross income
        # includes the gains, and the two parts deduct the losses.
        allowed_against_gains = model["capital_losses_allowed_against_gains"][i]
        net_loss = model["limited_capital_loss"][i]
        assert 0 <= net_loss <= limit, h
        assert net_loss == max(0, -expected), h
        gains = sum(
            max(0, p["long_term"] + p["short_term"]) + p["distributions"]
            for p in h["people"]
        )
        losses = sum(max(0, -(p["long_term"] + p["short_term"])) for p in h["people"])
        assert allowed_against_gains == min(losses, gains), h
        assert allowed_against_gains + net_loss == min(losses, gains + limit), h
        assert gains - allowed_against_gains - net_loss == expected, h
        # 3. Form 8960 line 5a.
        assert model["net_investment_income"][i] == expected, h
        # 4. Form 1040 line 16 routing (no qualified dividends here).
        line_15, line_16 = schedule_d_lines_15_16(h)
        assert bool(model["has_qdiv_or_ltcg"][i]) == (line_15 > 0 and line_16 > 0), h
        # 5. Person shares. A net loss is allocated in proportion to each
        # person's amount, a division that single precision rounds (for
        # example -3,000 split as 12/17 and 5/17 sums to -3,000.0002).
        n = len(h["people"])
        shares = model["person_share"][person : person + n].astype(float)
        assert abs(shares.sum() - expected) <= 0.01, h
        person += n
        # 6. The path without Schedule D.
        if all(p["long_term"] == 0 and p["short_term"] == 0 for p in h["people"]):
            distributions = sum(p["distributions"] for p in h["people"])
            assert expected == distributions
            assert allowed_against_gains == 0 and net_loss == 0, h


# ---------------------------------------------------------------------------
# A deterministic grid (runs without Hypothesis).
# ---------------------------------------------------------------------------

GRID_AMOUNTS = [-12_000, -5_000, -2_500, 0, 1_000, 4_000]
GRID_DISTRIBUTIONS = [0, 1_000, 3_000, 9_000]


def grid_households():
    households = []
    for lt, st_, d in itertools.product(GRID_AMOUNTS, GRID_AMOUNTS, GRID_DISTRIBUTIONS):
        person = {"long_term": lt, "short_term": st_, "distributions": d}
        households.append({"filing_status": "SINGLE", "people": [person]})
        households.append({"filing_status": "SEPARATE", "people": [person]})
        # The same totals split between spouses: the long-term amount and the
        # distributions with one spouse, the short-term amount with the other.
        households.append(
            {
                "filing_status": "JOINT",
                "people": [
                    {"long_term": lt, "short_term": 0, "distributions": d},
                    {"long_term": 0, "short_term": st_, "distributions": 0},
                ],
            }
        )
    return households


def test_grid():
    assert_properties(grid_households())


def test_example_from_the_schedule_d_instructions():
    """Long-term loss 5,000 and distributions 3,000: line 16 is -2,000, so
    the deductible loss is 2,000 (not 3,000 against gross income that still
    includes the distributions, which gave 0)."""
    h = {
        "filing_status": "SINGLE",
        "people": [{"long_term": -5_000, "short_term": 0, "distributions": 3_000}],
    }
    model = calculate([h])
    assert model["adjusted_gross_income"][0] == -2_000
    assert model["limited_capital_loss"][0] == 2_000


# ---------------------------------------------------------------------------
# Hypothesis.
# ---------------------------------------------------------------------------

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

AMOUNT = st.integers(min_value=-2_000_000, max_value=2_000_000)
SMALL = st.integers(min_value=-20_000, max_value=20_000)
DISTRIBUTIONS = st.one_of(
    st.just(0),
    st.integers(min_value=0, max_value=20_000),
    st.integers(min_value=0, max_value=2_000_000),
)


@st.composite
def person(draw):
    amounts = draw(st.sampled_from([AMOUNT, SMALL]))
    return {
        "long_term": draw(st.one_of(st.just(0), amounts)),
        "short_term": draw(st.one_of(st.just(0), amounts)),
        "distributions": draw(DISTRIBUTIONS),
    }


@st.composite
def household(draw):
    filing_status = draw(st.sampled_from(["SINGLE", "SEPARATE", "JOINT"]))
    n = 2 if filing_status == "JOINT" else 1
    return {
        "filing_status": filing_status,
        "people": [draw(person()) for _ in range(n)],
    }


@hypothesis.settings(max_examples=60, deadline=None)
@hypothesis.given(st.lists(household(), min_size=1, max_size=12))
def test_properties(households):
    assert_properties(households)


@hypothesis.settings(max_examples=40, deadline=None)
@hypothesis.given(
    st.lists(household(), min_size=1, max_size=8),
    st.integers(min_value=1, max_value=50_000),
)
def test_more_distributions_never_lower_agi(households, extra):
    """Adjusted gross income does not fall when distributions rise."""
    more = [
        {
            "filing_status": h["filing_status"],
            "people": [
                {
                    **h["people"][0],
                    "distributions": h["people"][0]["distributions"] + extra,
                }
            ]
            + h["people"][1:],
        }
        for h in households
    ]
    base = calculate(households)["adjusted_gross_income"]
    raised = calculate(more)["adjusted_gross_income"]
    assert (raised >= base).all()
    # And by no more than the extra distributions.
    assert (raised - base <= extra).all()


@hypothesis.settings(max_examples=40, deadline=None)
@hypothesis.given(st.lists(person(), min_size=1, max_size=10))
def test_dependent_modified_agi(dependents):
    """A dependent's own-return modified AGI (IRC 86(b)(2)) nets the
    distributions inside the single-filer limit."""
    people, tax_units, households_out = {}, {}, {}
    for i, p in enumerate(dependents):
        head, dep = f"head_{i}", f"dependent_{i}"
        people[head] = {"age": {YEAR: 45}, "is_tax_unit_head": {YEAR: True}}
        people[dep] = {
            "age": {YEAR: 70},
            "is_tax_unit_dependent": {YEAR: True},
            "is_tax_unit_spouse": {YEAR: False},
            "long_term_capital_gains": {YEAR: p["long_term"]},
            "short_term_capital_gains": {YEAR: p["short_term"]},
            "non_sch_d_capital_gains": {YEAR: p["distributions"]},
        }
        tax_units[f"tax_unit_{i}"] = {"members": [head, dep]}
        households_out[f"household_{i}"] = {
            "members": [head, dep],
            "state_code": {YEAR: "TX"},
        }
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households_out,
        }
    )
    magi = np.asarray(simulation.calculate("dependent_taxable_ss_magi", YEAR))
    agi = np.asarray(simulation.calculate("adjusted_gross_income", YEAR))
    for i, p in enumerate(dependents):
        total = p["long_term"] + p["short_term"] + p["distributions"]
        assert magi[2 * i + 1] == max(-3_000, total), p
        # The dependent's capital gains and losses stay off the head's return.
        assert agi[i] == 0, p
