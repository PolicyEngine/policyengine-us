"""Properties of the employer-plan bar on the self-employed health insurance deduction.

26 U.S.C. 162(l)(2)(B) and Form 7206 line 1 leave out premiums for any month
the taxpayer is eligible for a subsidized plan of their own or their spouse's
employer. The model's inputs are annual, so a person who has or is offered
employer coverage (`has_esi`, `offered_aca_disqualifying_esi`), or whose
employer pays some or all of the premiums, is eligible for the year, and so is
the other of the head and spouse on a joint return. A tax unit dependent is
barred only by their own coverage, never by a parent's.

Each batch places every drawn tax unit twice, once as drawn and once with every
coverage flag cleared, and runs as one vectorized baseline simulation. For
every tax unit and year:

1. Reference: each person's premium base equals a closed-form reference on
   the inputs: the person's premiums if they are self-employed and neither
   they nor (for the head and spouse) the other of the two is eligible, and 0
   otherwise.
2. Bounds: 0 <= deduction <= premium base <= premiums.
3. Monotone: clearing the coverage flags never lowers a person's premium base
   or deduction.
4. Differential: the flags move AGI only through the deduction, so the
   twins' AGI difference equals the difference in the head's and spouse's
   deductions.

A deterministic grid runs every combination of the head's, the spouse's and a
dependent's flags for a joint couple with a self-employed head.
Sources: https://www.law.cornell.edu/uscode/text/26/162#l_2_B and
https://www.irs.gov/pub/irs-prior/f7206--2025.pdf#page=1 (line 1).
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = [2024, 2025, 2026]
TOLERANCE = 0.01
CONTRIBUTIONS = ["NONE", "SOME", "ALL", "NA"]
EMPLOYER_PAYS = {"SOME", "ALL"}
NO_FLAGS = {"has_esi": False, "offered": False, "contribution": "NONE"}


def every_year(value):
    return {year: value for year in YEARS}


def own_eligible(flags):
    return (
        flags["has_esi"] or flags["offered"] or flags["contribution"] in EMPLOYER_PAYS
    )


def person_inputs(age, member, flags, dependent=False):
    inputs = {
        "age": every_year(age),
        "is_self_employed": every_year(member["self_employed"]),
        "self_employment_income": every_year(member["profit"]),
        "employment_income": every_year(member["wages"]),
        "health_insurance_premiums": every_year(member["premiums"]),
        "has_esi": every_year(flags["has_esi"]),
        "offered_aca_disqualifying_esi": every_year(flags["offered"]),
        "employer_contribution_to_health_insurance_premiums_category": every_year(
            flags["contribution"]
        ),
    }
    if dependent:
        inputs["is_tax_unit_dependent"] = every_year(True)
    return inputs


def build_situation(units):
    """Each unit twice: as drawn, then with every coverage flag cleared."""
    people, tax_units, households = {}, {}, {}
    rows = []  # per person: (premiums, self-employed, expected base, unit, twin)
    unit_index = 0
    for twin in (False, True):
        for i, unit in enumerate(units):
            name = f"u{i}_{'twin' if twin else 'drawn'}"
            members = unit["members"]
            flags = [NO_FLAGS if twin else m["flags"] for m in members]
            filers = [True, unit["joint"]][: min(2, len(members))]
            filers += [False] * (len(members) - len(filers))
            names = []
            for j, (member, member_flags) in enumerate(zip(members, flags)):
                person = f"{name}_p{j}"
                names.append(person)
                is_dependent = not filers[j]
                people[person] = person_inputs(
                    member["age"], member, member_flags, dependent=is_dependent
                )
            for j, member in enumerate(members):
                own = own_eligible(flags[j])
                other_filer = any(
                    own_eligible(flags[k])
                    for k in range(len(members))
                    if k != j and filers[k]
                )
                eligible = own or (filers[j] and other_filer)
                base = (
                    member["premiums"]
                    if member["self_employed"] and not eligible
                    else 0.0
                )
                rows.append(
                    (
                        member["premiums"],
                        member["self_employed"],
                        base,
                        unit_index,
                        twin,
                    )
                )
            tax_units[name] = {"members": names}
            households[name] = {"members": names, "state_code": every_year("TX")}
            unit_index += 1
    situation = {"people": people, "tax_units": tax_units, "households": households}
    premiums, self_employed, base, unit, twin = (np.array(c) for c in zip(*rows))
    return situation, premiums.astype(float), base.astype(float), unit, twin


def check_batch(units):
    situation, premiums, expected_base, unit, twin = build_situation(units)
    sim = Simulation(situation=situation)
    n = len(units)
    for year in YEARS:
        base = sim.calculate("self_employed_health_insurance_premiums", year)
        deduction = sim.calculate("self_employed_health_insurance_ald_person", year)
        # 1. Reference.
        np.testing.assert_allclose(base, expected_base, atol=TOLERANCE)
        # 2. Bounds.
        assert np.all(deduction >= -TOLERANCE)
        assert np.all(deduction <= base + TOLERANCE)
        assert np.all(base <= premiums + TOLERANCE)
        # 3. Monotone: the twin (no flags) of each person has at least as much.
        drawn, cleared = ~twin, twin
        assert np.all(base[cleared] >= base[drawn] - TOLERANCE)
        assert np.all(deduction[cleared] >= deduction[drawn] - TOLERANCE)
        # 4. Differential: AGI moves only through the head's and spouse's
        # deductions, which `self_employed_health_insurance_ald` sums.
        agi = sim.calculate("adjusted_gross_income", year)
        filer_deduction = sim.calculate("self_employed_health_insurance_ald", year)
        np.testing.assert_allclose(
            agi[:n] - agi[n:],
            filer_deduction[n:] - filer_deduction[:n],
            atol=TOLERANCE,
        )


flags_strategy = st.fixed_dictionaries(
    {
        "has_esi": st.booleans(),
        "offered": st.booleans(),
        "contribution": st.sampled_from(CONTRIBUTIONS),
    }
)
money = st.one_of(st.sampled_from([0, 1, 6_000]), st.integers(0, 40_000)).map(float)
profit = st.one_of(
    st.sampled_from([-5_000, 0, 433, 434, 50_000]), st.integers(-20_000, 250_000)
).map(float)


def member_strategy(age):
    return st.fixed_dictionaries(
        {
            "age": st.just(age),
            "self_employed": st.booleans(),
            "profit": profit,
            "wages": st.one_of(st.just(0.0), money),
            "premiums": money,
            "flags": flags_strategy,
        }
    )


unit_strategy = st.builds(
    lambda joint, head, spouse, dependents: {
        "joint": joint,
        "members": [head] + ([spouse] if joint else []) + dependents,
    },
    st.booleans(),
    member_strategy(45),
    member_strategy(43),
    st.lists(member_strategy(19), max_size=2),
)
SETTINGS = dict(
    max_examples=15,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(unit_strategy, min_size=4, max_size=12))
def test_premium_base_matches_the_form_7206_reference(units):
    check_batch(units)


ALL_FLAGS = [
    {"has_esi": has_esi, "offered": offered, "contribution": contribution}
    for has_esi, offered, contribution in itertools.product(
        [False, True], [False, True], CONTRIBUTIONS
    )
]


def grid_units():
    def member(age, self_employed, flags, premiums):
        return {
            "age": age,
            "self_employed": self_employed,
            "profit": 50_000.0 if self_employed else 0.0,
            "wages": 0.0 if self_employed else 30_000.0,
            "premiums": premiums,
            "flags": flags,
        }

    return [
        {
            "joint": True,
            "members": [
                member(45, True, head, 6_000.0),
                member(43, False, spouse, 0.0),
                member(19, False, dependent, 0.0),
            ],
        }
        for head, spouse, dependent in itertools.product(
            ALL_FLAGS, ALL_FLAGS, [NO_FLAGS, {**NO_FLAGS, "has_esi": True}]
        )
    ]


@pytest.fixture(scope="module")
def grid():
    units = grid_units()
    situation, premiums, expected_base, unit, twin = build_situation(units)
    return Simulation(situation=situation), units, expected_base, twin


@pytest.mark.parametrize("year", YEARS)
def test_grid_bars_on_head_or_spouse_coverage_only(grid, year):
    sim, units, expected_base, twin = grid
    base = sim.calculate("self_employed_health_insurance_premiums", year)
    np.testing.assert_allclose(base, expected_base, atol=TOLERANCE)
    head_base = base[~twin].reshape(len(units), 3)[:, 0]
    barred = np.array(
        [
            own_eligible(u["members"][0]["flags"])
            or own_eligible(u["members"][1]["flags"])
            for u in units
        ]
    )
    # The head's premiums count exactly when neither filer is eligible; the
    # dependent's coverage never matters.
    np.testing.assert_allclose(head_base, np.where(barred, 0, 6_000), atol=TOLERANCE)
    # Guard against a vacuous pass.
    assert barred.any() and (~barred).any()


@pytest.mark.parametrize("year", YEARS)
def test_grid_deduction_moves_agi_one_for_one(grid, year):
    sim, units, _, twin = grid
    n = len(units)
    agi = sim.calculate("adjusted_gross_income", year)
    deduction = sim.calculate("self_employed_health_insurance_ald", year)
    np.testing.assert_allclose(
        agi[:n] - agi[n:], deduction[n:] - deduction[:n], atol=TOLERANCE
    )
    # The twins all deduct the full $6,000; the earned income limit is higher.
    np.testing.assert_allclose(deduction[n:], 6_000, atol=TOLERANCE)
