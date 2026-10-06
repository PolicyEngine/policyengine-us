"""Invariants for dependents' income in the filer's EITC investment income test.

26 USC 32(i)(1) denies the credit when the "disqualified income of the
taxpayer" exceeds the limit. A tax unit dependent's interest, dividends,
capital gains, rents and passive income are on the dependent's own return, and
Publication 596 Worksheet 1 picks up a child's interest and dividends only
through a Form 8814 election, which the model does not implement. So
`eitc_relevant_investment_income` counts the head and spouse only, as
`irs_gross_income` does for AGI.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents), and a seeded population of 200
such units adds breadth. Dependents' capital gains are sometimes $16 million
or more, where float32 rounding of a tax unit total would show. Each batch runs
as one vectorized simulation three times: as drawn; with the dependents'
investment income inputs set to zero; and with $1,000 more of the head's
interest. For every tax unit:

1. The dependents' investment income, of any size or sign, never changes the
   filer's `eitc_relevant_investment_income`, `eitc_investment_income_eligible`,
   `eitc`, `filer_loss_limited_net_capital_gains` or AGI.
2. Differential: `eitc_relevant_investment_income` equals an independent numpy
   computation of Worksheet 1 over the head and spouse: interest, tax-exempt
   interest and dividends, plus their Schedule D gain with capital gain
   distributions floored at zero (line 7), plus their net rental and passive
   income floored at zero (line 13).
3. Bounds: it is at least the filers' interest and dividends (drawn
   nonnegative), so never negative, and $1,000 more of the head's interest
   raises it by exactly $1,000.
4. For tax units without dependents and without a negative distributions
   input, it equals the previous all-member formula, so leaving dependents out
   changes nothing for them. (With filer gains in the drawn range. Past about
   $16.8 million the previous formula's float32 tax unit total could be off by
   a few dollars, which the direct sum corrects.)

Gains are entered per person, so `net_capital_gains` is computed rather than
supplied; the YAML cases cover a supplied tax unit amount.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

PORTFOLIO_INPUTS = [
    "taxable_interest_income",
    "tax_exempt_interest_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
]
CAPITAL_INPUTS = ["long_term_capital_gains", "short_term_capital_gains"]
DISTRIBUTIONS = "non_sch_d_capital_gains"
# passive_partnership_s_corp_income is the passive subset of
# partnership_s_corp_income; both are drawn together below.
PASSIVE_INPUTS = ["rental_income", "passive_partnership_s_corp_income"]
# The filer's amounts, which a dependent's income must not change.
FILER_OUTPUTS = [
    "eitc_relevant_investment_income",
    "eitc_investment_income_eligible",
    "eitc",
    "filer_loss_limited_net_capital_gains",
    "adjusted_gross_income",
]
# Sums every member, for the previous formula in property 4.
OUTPUTS = FILER_OUTPUTS + ["net_capital_gains"]
# More of the head's interest, in the third run.
INTEREST_SHIFT = 1_000.0

nonnegative = st.one_of(st.just(0.0), st.integers(1, 8_000).map(float))
signed = st.one_of(st.just(0.0), st.integers(-12_000, 12_000).map(float))
# Up to $64 million either way, in multiples of 16 so float32 holds them
# exactly; a tax unit total above about $16.8 million rounds in float32.
very_large = st.integers(-4_000_000, 4_000_000).map(lambda x: 16.0 * x)


@st.composite
def investment_amounts(draw, dependent=False):
    passive = draw(signed)
    capital = st.one_of(signed, very_large) if dependent else signed
    return {
        **{name: draw(nonnegative) for name in PORTFOLIO_INPUTS},
        **{name: draw(capital) for name in CAPITAL_INPUTS},
        # Form 1099-DIV box 2a amounts are not negative, but the input can be;
        # the model floors each person's amount at zero.
        DISTRIBUTIONS: draw(st.one_of(nonnegative, st.integers(-3_000, -1).map(float))),
        "rental_income": draw(signed),
        "partnership_s_corp_income": passive,
        "passive_partnership_s_corp_income": passive,
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        # Wages where the credit is available, so eligibility moves eitc.
        "head_wages": float(draw(st.integers(0, 40_000))),
        "head": draw(investment_amounts()),
        "spouse": draw(investment_amounts()) if kind.startswith("joint") else None,
        "dependents": [
            {
                "age": draw(st.integers(1, 17)),
                **draw(investment_amounts(dependent=True)),
            }
            for _ in range(n_dependents)
        ],
    }


SEED = 20261006


def _seeded_amounts(rng, dependent=False):
    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def capital():
        if dependent and rng.random() < 0.2:
            return 16.0 * int(rng.integers(1_000_000, 4_000_000))
        return some(-12_000, 12_000)

    passive = some(-12_000, 12_000)
    return {
        **{name: some(1, 8_000) for name in PORTFOLIO_INPUTS},
        **{name: capital() for name in CAPITAL_INPUTS},
        DISTRIBUTIONS: some(-3_000, 8_000),
        "rental_income": some(-12_000, 12_000),
        "partnership_s_corp_income": passive,
        "passive_partnership_s_corp_income": passive,
    }


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head_wages": float(round(rng.uniform(0, 40_000))),
                "head": _seeded_amounts(rng),
                "spouse": (_seeded_amounts(rng) if kind.startswith("joint") else None),
                "dependents": [
                    {
                        "age": int(rng.integers(1, 18)),
                        **_seeded_amounts(rng, dependent=True),
                    }
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents=False, interest_shift=0.0):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 35,
            "is_tax_unit_head": True,
            "is_tax_unit_dependent": False,
            "employment_income": u["head_wages"],
            **u["head"],
            "taxable_interest_income": (
                u["head"]["taxable_interest_income"] + interest_shift
            ),
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": 33,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **u["spouse"],
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            amounts = {k: v for k, v in d.items() if k != "age"}
            if zero_dependents:
                amounts = {name: 0.0 for name in amounts}
            people[child] = {
                "age": d["age"],
                "is_tax_unit_dependent": True,
                **amounts,
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, **kwargs):
    sim = Simulation(situation=_situation(units, year, **kwargs))
    out = {name: np.asarray(sim.calculate(name, year), dtype=float) for name in OUTPUTS}
    out["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    eitc = sim.tax_benefit_system.parameters(f"{year}-01-01").gov.irs.credits.eitc
    out["limit"] = eitc.phase_out.max_investment_income
    return out


def _by_person(units, key):
    """Person-level input values (or the dependent flag) in member order."""
    rows = []
    for u in units:
        rows.append((u["head"], False))
        if u["spouse"] is not None:
            rows.append((u["spouse"], False))
        rows += [(amounts, True) for amounts in u["dependents"]]
    if key == "is_dependent":
        return np.array([dependent for _, dependent in rows])
    return np.array([amounts[key] for amounts, _ in rows])


def _unit_sum(run, values):
    return np.bincount(
        run["unit"],
        weights=values,
        minlength=len(run["eitc_relevant_investment_income"]),
    )


def _check(units, year):
    run = _run(units, year)
    zeroed = _run(units, year, zero_dependents=True)
    shifted = _run(units, year, interest_shift=INTEREST_SHIFT)
    filer = ~_by_person(units, "is_dependent")
    assert np.array_equal(~run["is_dependent"], filer)
    has_dependent = _unit_sum(run, (~filer).astype(float)) > 0

    # 1. The dependents' investment income never reaches the filer's test.
    for name in FILER_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )

    # 2. Differential: Worksheet 1 over the head and spouse, from the inputs.
    def filer_sum(names):
        return _unit_sum(run, filer * sum(_by_person(units, n) for n in names))

    portfolio = filer_sum(PORTFOLIO_INPUTS)
    distributions = _unit_sum(
        run, filer * np.maximum(0, _by_person(units, DISTRIBUTIONS))
    )
    capital = np.maximum(0, filer_sum(CAPITAL_INPUTS) + distributions)
    passive = np.maximum(0, filer_sum(PASSIVE_INPUTS))
    expected = portfolio + capital + passive
    investment_income = run["eitc_relevant_investment_income"]
    np.testing.assert_allclose(investment_income, expected, atol=TOLERANCE)
    np.testing.assert_array_equal(
        run["eitc_investment_income_eligible"].astype(bool),
        expected <= run["limit"],
    )
    assert not (run["eitc"][expected > run["limit"]] > 0).any()

    # 3. Bounds and an exact shift in the filer's interest.
    assert (investment_income >= portfolio - TOLERANCE).all()
    assert (investment_income >= -TOLERANCE).all()
    np.testing.assert_allclose(
        shifted["eitc_relevant_investment_income"] - investment_income,
        INTEREST_SHIFT,
        atol=TOLERANCE,
    )

    # 4. No dependents and no negative distributions input: the previous
    # all-member formula, unchanged.
    no_negative_distributions = (
        _unit_sum(run, (_by_person(units, DISTRIBUTIONS) < 0).astype(float)) == 0
    )
    unchanged = ~has_dependent & no_negative_distributions
    all_member = (
        _unit_sum(run, sum(_by_person(units, n) for n in PORTFOLIO_INPUTS))
        + np.maximum(
            0,
            run["net_capital_gains"] + _unit_sum(run, _by_person(units, DISTRIBUTIONS)),
        )
        + np.maximum(
            0, _unit_sum(run, sum(_by_person(units, n) for n in PASSIVE_INPUTS))
        )
    )
    np.testing.assert_allclose(
        investment_income[unchanged], all_member[unchanged], atol=TOLERANCE
    )
    return has_dependent, unchanged


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_dependent_investment_income_stays_off_the_filers_eitc_test(units):
    _check(units, 2025)


@pytest.mark.parametrize("year", [2021, 2025])
def test_seeded_population(year):
    has_dependent, unchanged = _check(_seeded_units(), year)
    # The population exercises both branches of each property.
    assert has_dependent.sum() > 50
    assert unchanged.sum() > 20


def test_unsupplied_net_capital_gains_is_not_read_as_an_aggregate():
    # net_capital_gains can hold a value that was neither supplied nor the
    # members' current gains: abolished (gov.abolitions.net_capital_gains
    # makes it 0), or calculated before an input changed, as here. Only a
    # supplied amount is read as an aggregate, so the capital gain line stays
    # the filers' own gains and the dependent's gain changes nothing. A
    # reform simulation would cost a parameter-tree copy; the cached value
    # reaches the same branch.
    year = 2025
    situation = {
        "people": {
            "head": {
                "age": {year: 30},
                "employment_income": {year: 20_000},
                "taxable_interest_income": {year: 7_000},
                DISTRIBUTIONS: {year: 5_000},
            },
            "child": {
                "age": {year: 8},
                "is_tax_unit_dependent": {year: True},
                "long_term_capital_gains": {year: 0},
            },
        },
        "tax_units": {"tax_unit": {"members": ["head", "child"]}},
        "households": {
            "household": {"members": ["head", "child"], "state_code": {year: "TX"}}
        },
    }
    sim = Simulation(situation=situation)
    # The formula lists net_capital_gains' components itself; keep them in
    # step.
    assert sim.tax_benefit_system.get_variable("net_capital_gains").adds == [
        "long_term_capital_gains",
        "short_term_capital_gains",
    ]
    assert sim.calculate("net_capital_gains", year)[0] == 0
    sim.set_input("long_term_capital_gains", year, np.array([0, 5_000]))
    # 7,000 of interest + max(0, 0 + 5,000 of distributions).
    assert sim.calculate("eitc_relevant_investment_income", year)[0] == 12_000
