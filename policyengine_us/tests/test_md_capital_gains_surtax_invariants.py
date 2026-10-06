"""Invariants for Maryland's additional 2% tax on net capital gain.

Md. Code, Tax-General 10-105(a)(3) taxes 2% of the "net capital gain, as
defined and determined under the Internal Revenue Code" included in Maryland
adjusted gross income, less the gain from excepted assets, and (a)(4)
applies it when federal adjusted gross income is over $350,000. Net capital
gain is 26 U.S.C. 1222(11): the net long-term capital gain less the net
short-term capital loss. Over the head and spouse, with long-term (LT) and
short-term (ST) gains and losses and capital gain distributions reported
without Schedule D (D):

    L15 = sum(LT + max(0, D))      Schedule D line 15
    L16 = L15 + sum(ST)            Schedule D line 16
    NCG = max(0, min(L15, L16))    Form 502CG line 1

The properties below hold for every household:

1. md_net_capital_gain equals NCG, computed here from the inputs.
2. Differential: for a return with no dependents and no negative
   distributions, md_net_capital_gain equals the federal net_capital_gain
   (a separate 1222(11) implementation) less qualified dividends, which
   section 1(h)(11) adds only for section 1(h).
3. md_net_capital_gain never exceeds the positive part of the filers' Form
   1040 line 7a gain (filer_loss_limited_net_capital_gains), so it is all
   included in federal, and hence Maryland, adjusted gross income.
4. The surtax applies exactly when federal adjusted gross income is over
   $350,000, and is then 2% of max(0, NCG - excepted gain) (Form 502CG line
   9); otherwise it is zero. It is between 0 and 2% of NCG.
5. Changing a dependent's gains, losses or distributions changes neither
   md_net_capital_gain nor the surtax.
6. Raising a filer's LT, ST or D by x raises md_net_capital_gain by between
   0 and x, and a net short-term gain adds nothing. Raising the excepted gain
   never raises the surtax.
7. The surtax enters Maryland income tax before credits once: neutralizing
   it lowers that tax by exactly the surtax.

Amounts are whole dollars below $2,000,000, so every sum is exact in single
precision; only the 2% products are compared with a cent of tolerance.
"""

import itertools

import numpy as np
import pytest

from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2025
RATE = 0.02
THRESHOLD = 350_000
TOLERANCE = 0.01
AGES = {"head": 45, "spouse": 43, "dependent": 10}


class neutralize_md_capital_gains_surtax(Reform):
    def apply(self):
        self.neutralize_variable("md_capital_gains_surtax")


def person(role, lt=0, st=0, d=0, qd=0, wages=0):
    return dict(role=role, lt=lt, st=st, d=d, qd=qd, wages=wages)


def household(people, excepted=0):
    return dict(people=people, excepted=excepted)


def filers(h):
    return [p for p in h["people"] if p["role"] != "dependent"]


def reference_net_capital_gain(h):
    line_15 = sum(p["lt"] + max(0, p["d"]) for p in filers(h))
    line_16 = line_15 + sum(p["st"] for p in filers(h))
    return max(0, min(line_15, line_16))


def build_situation(households):
    y = str(YEAR)
    people, tax_units, marital_units, households_out = {}, {}, {}, {}
    for i, h in enumerate(households):
        members = []
        adults = []
        for j, p in enumerate(h["people"]):
            name = f"p_{i}_{j}"
            people[name] = {
                "age": {y: AGES[p["role"]]},
                "long_term_capital_gains": {y: p["lt"]},
                "short_term_capital_gains": {y: p["st"]},
                "non_sch_d_capital_gains": {y: p["d"]},
                "qualified_dividend_income": {y: p["qd"]},
                "employment_income": {y: p["wages"]},
            }
            members.append(name)
            if p["role"] == "dependent":
                marital_units[f"mu_{i}_{j}"] = {"members": [name]}
            else:
                adults.append(name)
        marital_units[f"mu_{i}"] = {"members": adults}
        # Set on every unit: an input given for some units gives the others
        # its default.
        tax_units[f"tu_{i}"] = {
            "members": members,
            "md_capital_gains_surtax_excepted_gain": {y: h["excepted"]},
        }
        households_out[f"hh_{i}"] = {
            "members": members,
            "state_code": {y: "MD"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households_out,
    }


TAX_UNIT_OUTPUTS = [
    "md_net_capital_gain",
    "md_capital_gains_surtax",
    "md_capital_gains_surtax_applies",
    "adjusted_gross_income",
    "net_capital_gain",
    "filer_loss_limited_net_capital_gains",
    "md_income_tax_before_credits",
]


def calculate(households, neutralized=False):
    situation = build_situation(households)
    simulation = Simulation(situation=situation)
    out = {v: np.asarray(simulation.calculate(v, YEAR)) for v in TAX_UNIT_OUTPUTS}
    dependent = np.asarray(simulation.calculate("is_tax_unit_dependent", YEAR))
    roles = [p["role"] for h in households for p in h["people"]]
    # Guard the fixture: the model must see the roles the reference assumes.
    assert list(dependent) == [r == "dependent" for r in roles]
    if neutralized:
        without = Simulation(
            situation=situation, reform=neutralize_md_capital_gains_surtax
        )
        out["md_tax_without_surtax"] = np.asarray(
            without.calculate("md_income_tax_before_credits", YEAR)
        )
    return out


def assert_single_household_properties(h, r, i):
    ncg = reference_net_capital_gain(h)
    # 1. Form 502CG line 1.
    assert r["md_net_capital_gain"][i] == ncg, h
    # 2. Differential with the federal 1222(11) path.
    no_dependents = len(filers(h)) == len(h["people"])
    if no_dependents and all(p["d"] >= 0 for p in h["people"]):
        qualified_dividends = sum(p["qd"] for p in h["people"])
        assert r["md_net_capital_gain"][i] == (
            r["net_capital_gain"][i] - qualified_dividends
        ), h
    # 3. Included in adjusted gross income.
    assert r["md_net_capital_gain"][i] <= max(
        0, r["filer_loss_limited_net_capital_gains"][i]
    ), h
    # 4. Threshold on federal AGI, and Form 502CG line 9.
    over = r["adjusted_gross_income"][i] > THRESHOLD
    assert bool(r["md_capital_gains_surtax_applies"][i]) == over, h
    expected = RATE * max(0, ncg - h["excepted"]) if over else 0
    surtax = float(r["md_capital_gains_surtax"][i])
    assert abs(surtax - expected) <= TOLERANCE, h
    assert -TOLERANCE <= surtax <= RATE * ncg + TOLERANCE, h
    # 7. Added once to Maryland income tax before credits.
    if "md_tax_without_surtax" in r:
        added = float(r["md_income_tax_before_credits"][i]) - float(
            r["md_tax_without_surtax"][i]
        )
        assert abs(added - surtax) <= TOLERANCE, h


def with_change(h, role, field, delta):
    people = [dict(p) for p in h["people"]]
    for p in people:
        if p["role"] == role:
            p[field] += delta
            break
    return household(people, h["excepted"])


def twins(h, delta):
    """Households paired with h for properties 5 and 6."""
    pairs = []
    if any(p["role"] == "dependent" for p in h["people"]):
        for field in ["lt", "st", "d"]:
            pairs.append(
                ("dependent", field, with_change(h, "dependent", field, delta))
            )
    for field in ["lt", "st", "d"]:
        pairs.append(("head", field, with_change(h, "head", field, delta)))
    pairs.append(("excepted", None, household(h["people"], h["excepted"] + delta)))
    return pairs


def assert_properties(households, delta, neutralized=False):
    batch, index = [], []
    for h in households:
        base = len(batch)
        batch.append(h)
        for kind, field, twin in twins(h, delta):
            index.append((base, len(batch), kind, field))
            batch.append(twin)
    r = calculate(batch, neutralized=neutralized)
    for i, h in enumerate(batch):
        assert_single_household_properties(h, r, i)
    ncg = r["md_net_capital_gain"].astype(float)
    surtax = r["md_capital_gains_surtax"].astype(float)
    for base, twin, kind, field in index:
        if kind == "dependent":
            # 5. Dependent invariance.
            assert ncg[twin] == ncg[base], batch[twin]
            assert surtax[twin] == surtax[base], batch[twin]
        elif kind == "head":
            # 6. Monotone, with slope at most 1.
            change = ncg[twin] - ncg[base]
            assert 0 <= change <= delta, (batch[base], field)
            if field == "st" and sum(p["st"] for p in filers(batch[base])) >= 0:
                # A net short-term gain adds nothing.
                assert change == 0, (batch[base], field)
        else:
            assert surtax[twin] <= surtax[base] + TOLERANCE, batch[twin]


# ---------------------------------------------------------------------------
# A deterministic grid (runs without Hypothesis).
# ---------------------------------------------------------------------------

LT = [-60_000, -5_000, 0, 40_000, 250_000]
ST = [-80_000, -10_000, 0, 30_000]
D = [-2_000, 0, 7_000]


def grid_households():
    households = []
    for lt, st_, d in itertools.product(LT, ST, D):
        # A single filer near and over the threshold.
        for wages in [200_000, 400_000]:
            households.append(household([person("head", lt, st_, d, wages=wages)]))
        # The same totals split between spouses, with qualified dividends.
        households.append(
            household(
                [
                    person("head", lt=lt, d=d, qd=5_000, wages=380_000),
                    person("spouse", st=st_),
                ]
            )
        )
        # A head with a dependent who has the same amounts, and an excepted
        # gain.
        households.append(
            household(
                [
                    person("head", lt, st_, d, wages=420_000),
                    person("dependent", lt=lt, st=st_, d=abs(d)),
                ],
                excepted=20_000,
            )
        )
    return households


def test_grid():
    assert_properties(grid_households(), delta=15_000, neutralized=True)


def test_cases_where_the_form_1040_line_7a_gain_differs():
    """A net short-term gain, and a net long-term loss with a short-term
    gain: line 7a counts both, net capital gain neither."""
    cases = [
        household([person("head", lt=100_000, st=50_000, wages=400_000)]),
        household([person("head", lt=-10_000, st=50_000, wages=400_000)]),
        household([person("head", st=80_000, wages=400_000)]),
    ]
    r = calculate(cases)
    assert list(r["md_net_capital_gain"]) == [100_000, 0, 0]
    assert list(r["filer_loss_limited_net_capital_gains"]) == [150_000, 40_000, 80_000]
    assert list(r["md_capital_gains_surtax"]) == [2_000, 0, 0]


# ---------------------------------------------------------------------------
# Hypothesis properties (Hypothesis is a dev extra).
# ---------------------------------------------------------------------------

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

GAIN = st.integers(min_value=-300_000, max_value=300_000)
DISTRIBUTIONS = st.integers(min_value=-5_000, max_value=50_000)
DIVIDENDS = st.integers(min_value=0, max_value=50_000)
WAGES = st.integers(min_value=0, max_value=800_000)


@st.composite
def random_household(draw):
    def filer(role):
        return person(
            role,
            draw(GAIN),
            draw(GAIN),
            draw(DISTRIBUTIONS),
            draw(DIVIDENDS),
            draw(WAGES),
        )

    people = [filer("head")]
    if draw(st.booleans()):
        people.append(filer("spouse"))
    for _ in range(draw(st.integers(min_value=0, max_value=2))):
        people.append(person("dependent", draw(GAIN), draw(GAIN), draw(DISTRIBUTIONS)))
    excepted = draw(st.sampled_from([0, 0, 10_000, draw(GAIN.map(abs))]))
    return household(people, excepted)


@hypothesis.settings(max_examples=25, deadline=None)
@hypothesis.given(
    st.lists(random_household(), min_size=1, max_size=8),
    st.integers(min_value=1, max_value=100_000),
)
def test_properties(households, delta):
    assert_properties(households, delta)
