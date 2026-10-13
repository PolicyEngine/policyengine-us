"""Invariants for passive estate and trust income in the EITC investment income test.

Publication 596 Worksheet 1 lines 11 and 12 name Schedule E line 34a column
(d) and line 34b column (c), the passive income and loss from estates and
trusts, and line 13 nets every passive activity of the head and spouse and
floors the result at zero. The nonpassive columns (e) and (f) are not named.
`passive_estate_income` is the passive subset of `estate_income` (the Part III
total in AGI) and defaults to zero.

Hypothesis draws batches of single and joint tax units, and a seeded
population of 200 adds breadth. Each batch runs as one vectorized simulation
four times: as drawn; with every member's estate_income moved by an unrelated
signed amount while passive_estate_income stays put; with the head's passive
estate income raised by a nonnegative amount; and with passive_estate_income
set to zero explicitly for every member who left it unset. For every tax unit:

1. Only the passive subset counts: moving estate_income alone (the nonpassive
   part) never changes eitc_relevant_investment_income or
   eitc_investment_income_eligible, though it does move AGI.
2. Monotone and 1-Lipschitz: raising the head's passive estate income by
   delta >= 0 raises eitc_relevant_investment_income by at least 0 and at most
   delta, and by exactly delta when the filers' passive basket was already
   nonnegative.
3. Basket isolation: a passive estate or trust loss never takes investment
   income below the filers' interest plus their capital gains floored at zero,
   and investment income never exceeds that plus the positive passive amounts.
4. The default is zero for each person on their own: leaving
   passive_estate_income unset for some members, while others set it, gives the
   same result as setting it to zero for them.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
ESTATE = "estate_income"
PASSIVE_ESTATE = "passive_estate_income"
OUTPUTS = [
    "eitc_relevant_investment_income",
    "eitc_investment_income_eligible",
    "adjusted_gross_income",
]

nonnegative = st.one_of(st.just(0.0), st.integers(1, 9_000).map(float))
signed = st.one_of(st.just(0.0), st.integers(-12_000, 12_000).map(float))


@st.composite
def person_amounts(draw):
    estate = draw(signed)
    amounts = {
        "taxable_interest_income": draw(nonnegative),
        "long_term_capital_gains": draw(signed),
        "rental_income": draw(signed),
        ESTATE: estate,
        # The nonpassive move in the second run.
        "estate_shift": draw(signed),
    }
    passive = draw(
        st.one_of(
            st.none(),
            st.just(estate),
            st.just(float(round(estate / 2))),
            signed,
        )
    )
    if passive is not None:
        amounts[PASSIVE_ESTATE] = passive
    return amounts


@st.composite
def tax_units(draw):
    joint = draw(st.booleans())
    return {
        "head_wages": float(draw(st.integers(0, 40_000))),
        "head": draw(person_amounts()),
        "spouse": draw(person_amounts()) if joint else None,
        "passive_shift": float(draw(st.integers(0, 15_000))),
    }


SEED = 20261013


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.6):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def person():
        estate = some(-12_000, 12_000, 0.8)
        amounts = {
            "taxable_interest_income": some(1, 9_000),
            "long_term_capital_gains": some(-12_000, 12_000),
            "rental_income": some(-12_000, 12_000),
            ESTATE: estate,
            "estate_shift": some(-12_000, 12_000, 0.9),
        }
        choice = rng.choice(["unset", "all", "half", "other"])
        if choice != "unset":
            amounts[PASSIVE_ESTATE] = {
                "all": estate,
                "half": float(round(estate / 2)),
                "other": some(-12_000, 12_000, 1),
            }[choice]
        return amounts

    return [
        {
            "head_wages": float(round(rng.uniform(0, 40_000))),
            "head": person(),
            "spouse": person() if rng.random() < 0.5 else None,
            "passive_shift": float(round(rng.uniform(0, 15_000))),
        }
        for _ in range(n)
    ]


def _person_inputs(amounts, *, shift_estate, explicit_zero):
    values = {k: v for k, v in amounts.items() if k != "estate_shift"}
    if shift_estate:
        values[ESTATE] += amounts["estate_shift"]
    if explicit_zero:
        values.setdefault(PASSIVE_ESTATE, 0.0)
    return values


def _situation(
    units,
    year,
    *,
    shift_estate=False,
    shift_passive=False,
    explicit_zero=False,
):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    flags = dict(shift_estate=shift_estate, explicit_zero=explicit_zero)
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 35,
            "is_tax_unit_head": True,
            "employment_income": u["head_wages"],
            **_person_inputs(u["head"], **flags),
        }
        if shift_passive:
            people[head][PASSIVE_ESTATE] = (
                people[head].get(PASSIVE_ESTATE, 0.0) + u["passive_shift"]
            )
        members = [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": 33,
                "is_tax_unit_spouse": True,
                **_person_inputs(u["spouse"], **flags),
            }
            members.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": members}
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
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float) for name in OUTPUTS
    }


def _filer_sum(units, value):
    """Sum value(amounts) over each unit's head and spouse."""
    return np.array(
        [
            value(u["head"]) + (value(u["spouse"]) if u["spouse"] is not None else 0)
            for u in units
        ]
    )


def _check(units, year):
    run = _run(units, year)
    nonpassive_moved = _run(units, year, shift_estate=True)
    passive_raised = _run(units, year, shift_passive=True)
    explicit = _run(units, year, explicit_zero=True)
    investment_income = run["eitc_relevant_investment_income"]

    # 1. Only the passive subset counts.
    for name in ["eitc_relevant_investment_income", "eitc_investment_income_eligible"]:
        np.testing.assert_allclose(
            nonpassive_moved[name], run[name], atol=TOLERANCE, err_msg=name
        )
    # The moved amount is real income: it reaches AGI somewhere in the batch.
    estate_moved = _filer_sum(units, lambda a: a["estate_shift"]) != 0
    agi_moved = np.abs(
        nonpassive_moved["adjusted_gross_income"] - run["adjusted_gross_income"]
    )
    if estate_moved.any():
        assert (agi_moved[estate_moved] > TOLERANCE).any()

    # 2. Monotone and 1-Lipschitz in the head's passive estate income.
    shift = np.array([u["passive_shift"] for u in units])
    change = passive_raised["eitc_relevant_investment_income"] - investment_income
    assert (change >= -TOLERANCE).all()
    assert (change <= shift + TOLERANCE).all()
    passive_basket = _filer_sum(
        units, lambda a: a["rental_income"] + a.get(PASSIVE_ESTATE, 0.0)
    )
    already_nonnegative = passive_basket >= 0
    np.testing.assert_allclose(
        change[already_nonnegative], shift[already_nonnegative], atol=TOLERANCE
    )

    # 3. Basket isolation.
    portfolio = _filer_sum(units, lambda a: a["taxable_interest_income"])
    capital = np.maximum(0, _filer_sum(units, lambda a: a["long_term_capital_gains"]))
    positive_passive = _filer_sum(
        units,
        lambda a: max(0, a["rental_income"]) + max(0, a.get(PASSIVE_ESTATE, 0.0)),
    )
    assert (investment_income >= portfolio + capital - TOLERANCE).all()
    assert (
        investment_income <= portfolio + capital + positive_passive + TOLERANCE
    ).all()

    # 4. Unset means zero for that person, even when others set it.
    for name in OUTPUTS:
        np.testing.assert_allclose(
            explicit[name], run[name], atol=TOLERANCE, err_msg=name
        )
    mixed = np.array(
        [
            u["spouse"] is not None
            and (PASSIVE_ESTATE in u["head"]) != (PASSIVE_ESTATE in u["spouse"])
            for u in units
        ]
    )
    passive_floored = passive_basket < 0
    return mixed, passive_floored


SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_passive_estate_income_in_the_eitc_passive_basket(units):
    _check(units, 2024)


@pytest.mark.parametrize("year", [2024, 2026])
def test_seeded_population(year):
    mixed, passive_floored = _check(_seeded_units(), year)
    # The population has units where only one spouse sets the input, and units
    # whose passive basket is floored at zero.
    assert mixed.sum() > 10
    assert passive_floored.sum() > 10
