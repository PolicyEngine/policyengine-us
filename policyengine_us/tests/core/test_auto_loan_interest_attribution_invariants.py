"""Invariants for attributing car loan interest to tax units.

26 U.S.C. 163(h)(4)(B)(i) counts interest "on indebtedness incurred by the
taxpayer", and 26 CFR 1.163-16(h)(1) limits it to $10,000 "per Federal tax
return regardless of filing status". The model takes each person's own loans
(qualified_passenger_vehicle_loan_interest_person, for the tax unit head and
spouse) and a household-level amount that goes in full to the tax unit of the
household head (the oldest member when no head is designated, the older flagged
head when several are).

Invariants, for every household of one to four tax units, written from the
statute and the regulation rather than read from the model's parameters:

1. Conservation: the household's tax units together hold the household amount
   plus every head's and spouse's own interest. Nothing is counted twice and
   only a dependent's own interest is dropped.
2. One holder: the household amount lands on exactly one tax unit, the one
   holding the designated (or fallback) household head.
3. Locality: a tax unit's deduction depends only on its own filers' loans and
   on the household amount when it holds the head. Zeroing other tax units'
   loans leaves it unchanged.
4. Differential against the statute: the deduction is
   max(min(interest, 10,000) - 200 x ceil(max(MAGI - threshold, 0) / 1,000), 0),
   with a $200,000 threshold for a joint return and $100,000 otherwise.
5. Bounds: 0 <= deduction <= min(tax unit interest, 10,000).
"""

import math

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
CAP = 10_000  # 26 U.S.C. 163(h)(4)(C)(i)
THRESHOLD = {"JOINT": 200_000}  # 163(h)(4)(C)(ii)(I); 100,000 otherwise
OTHER_THRESHOLD = 100_000
STEP, INCREMENT = 200, 1_000
KINDS = ["single", "joint", "hoh", "joint_with_child", "adult_dependent"]
# Each kind's dependent, if any, and its age range. An adult dependent (a
# student, an elderly parent) can hold their own loan and be the household's
# oldest member.
DEPENDENT_AGES = {
    "hoh": (1, 17),
    "joint_with_child": (1, 17),
    "adult_dependent": (18, 90),
}


def money(high):
    return st.one_of(st.just(0.0), st.integers(1, high).map(float))


@st.composite
def tax_unit_specs(draw):
    kind = draw(st.sampled_from(KINDS))
    adults = 2 if kind.startswith("joint") else 1
    dependents = 1 if kind in DEPENDENT_AGES else 0
    people = []
    for i in range(adults + dependents):
        is_dependent = i >= adults
        ages = DEPENDENT_AGES[kind] if is_dependent else (18, 90)
        people.append(
            {
                "age": draw(st.integers(*ages)),
                "dependent": is_dependent,
                "wages": 0.0 if is_dependent else draw(money(260_000)),
                "interest": draw(money(12_000)),
                "head_flag": draw(st.sampled_from([False, False, False, True])),
            }
        )
    return {"kind": kind, "people": people}


@st.composite
def household_specs(draw):
    return {
        "tax_units": draw(st.lists(tax_unit_specs(), min_size=1, max_size=4)),
        "amount": draw(money(16_000)),
    }


def _seeded_households(n=80, seed=20261023, ties=True):
    rng = np.random.default_rng(seed)

    def some(high, p=0.6):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    households = []
    for h in range(n):
        units = []
        for _ in range(int(rng.integers(1, 5))):
            kind = str(rng.choice(KINDS))
            adults = 2 if kind.startswith("joint") else 1
            dependents = 1 if kind in DEPENDENT_AGES else 0
            low, high = DEPENDENT_AGES.get(kind, (18, 90))
            units.append(
                {
                    "kind": kind,
                    "people": [
                        {
                            "age": int(rng.integers(low, high + 1))
                            if i >= adults
                            else int(rng.integers(18, 91)),
                            "dependent": i >= adults,
                            "wages": 0.0 if i >= adults else some(260_000, 0.9),
                            "interest": some(12_000, 0.5),
                            # A third of households flag no head, so the
                            # oldest-member fallback runs beside flagged ones.
                            "head_flag": bool(h % 3) and rng.random() < 0.3,
                        }
                        for i in range(adults + dependents)
                    ],
                }
            )
        households.append({"tax_units": units, "amount": some(16_000, 0.7)})
    if not ties:
        # Distinct ages within each household, so the holder is unambiguous
        # whatever order the members are listed in.
        for household in households:
            seen = set()
            for unit in household["tax_units"]:
                for p in unit["people"]:
                    while p["age"] in seen:
                        p["age"] += 1
                    seen.add(p["age"])
        return households
    # Ties: two 40-year-old roommates, no head flagged; and two flagged
    # heads of the same age. The first listed takes the household amount.
    tie = {"age": 40, "dependent": False, "wages": 50_000.0, "interest": 0.0}
    households.append(
        {
            "tax_units": [
                {"kind": "single", "people": [dict(tie, head_flag=False)]},
                {"kind": "single", "people": [dict(tie, head_flag=False)]},
            ],
            "amount": 5_000.0,
        }
    )
    households.append(
        {
            "tax_units": [
                {"kind": "single", "people": [dict(tie, head_flag=True)]},
                {"kind": "single", "people": [dict(tie, head_flag=True)]},
            ],
            "amount": 5_000.0,
        }
    )
    return households


def _situation(households, year, shuffle_seed=None):
    people, tax_units, marital_units, spm_units, hh = {}, {}, {}, {}, {}
    for h, household in enumerate(households):
        members = []
        for t, unit in enumerate(household["tax_units"]):
            unit_members = []
            for i, p in enumerate(unit["people"]):
                name = f"p_{h}_{t}_{i}"
                people[name] = {
                    "age": {year: p["age"]},
                    "employment_income": {year: p["wages"]},
                    "qualified_passenger_vehicle_loan_interest_person": {
                        year: p["interest"]
                    },
                    "is_tax_unit_dependent": {year: p["dependent"]},
                    "is_household_head": {year: p["head_flag"]},
                }
                unit_members.append(name)
            tax_units[f"t_{h}_{t}"] = {"members": unit_members}
            adults = [
                m for m, p in zip(unit_members, unit["people"]) if not p["dependent"]
            ]
            marital_units[f"m_{h}_{t}"] = {"members": adults}
            for m, p in zip(unit_members, unit["people"]):
                if p["dependent"]:
                    marital_units[f"m_{m}"] = {"members": [m]}
            spm_units[f"s_{h}_{t}"] = {"members": unit_members}
            members += unit_members
        hh[f"h_{h}"] = {
            "members": members,
            "state_code": {year: "TX"},
            "qualified_passenger_vehicle_loan_interest": {year: household["amount"]},
        }
    if shuffle_seed is not None:
        names = list(people)
        order = np.random.default_rng(shuffle_seed).permutation(len(names))
        people = {names[i]: people[names[i]] for i in order}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "households": hh,
    }


def _holder(household):
    """(tax unit index) holding the household amount, from the rule's text."""
    flat = [
        (t, p) for t, unit in enumerate(household["tax_units"]) for p in unit["people"]
    ]
    flagged = [(t, p) for t, p in flat if p["head_flag"]]
    pool = flagged or flat
    # Oldest first; ties go to the first listed (max returns the first).
    return max(pool, key=lambda tp: tp[1]["age"])[0]


def _expected_interest(households):
    expected = []
    for household in households:
        holder = _holder(household)
        for t, unit in enumerate(household["tax_units"]):
            own = sum(p["interest"] for p in unit["people"] if not p["dependent"])
            expected.append(own + (household["amount"] if t == holder else 0.0))
    return np.array(expected)


def _statute_deduction(interest, magi, filing_status):
    out = []
    for i, m, fs in zip(interest, magi, filing_status):
        threshold = THRESHOLD.get(fs, OTHER_THRESHOLD)
        steps = math.ceil(max(m - threshold, 0) / INCREMENT)
        out.append(max(min(i, CAP) - STEP * steps, 0))
    return np.array(out)


def _calculate(households, year, shuffle_seed=None):
    sim = Simulation(situation=_situation(households, year, shuffle_seed))
    return {
        "interest": sim.calculate(
            "tax_unit_qualified_passenger_vehicle_loan_interest", year
        ),
        "deduction": sim.calculate("auto_loan_interest_deduction", year),
        "magi": sim.calculate("agi_plus_section_911_931_933_exclusions", year),
        "filing_status": sim.calculate("filing_status", year).decode_to_str(),
    }


def _check(households, year, shuffle_seed=None):
    result = _calculate(households, year, shuffle_seed)
    interest, deduction = result["interest"], result["deduction"]
    expected = _expected_interest(households)

    # 2. One holder, and the tax unit totals are exactly the rule's.
    np.testing.assert_allclose(interest, expected, atol=TOLERANCE)

    # 1. Conservation per household.
    start = 0
    for household in households:
        n = len(household["tax_units"])
        filers_own = sum(
            p["interest"]
            for unit in household["tax_units"]
            for p in unit["people"]
            if not p["dependent"]
        )
        assert (
            abs(interest[start : start + n].sum() - (household["amount"] + filers_own))
            < TOLERANCE
        )
        start += n

    # 4. Differential against the statute.
    np.testing.assert_allclose(
        deduction,
        _statute_deduction(expected, result["magi"], result["filing_status"]),
        atol=TOLERANCE,
    )

    # 5. Bounds.
    assert (deduction >= -TOLERANCE).all()
    assert (deduction <= np.minimum(interest, CAP) + TOLERANCE).all()
    return result


def _zero_odd_units(households):
    """Copy with every odd-numbered tax unit's own loans set to zero."""
    out = []
    for household in households:
        units = []
        for t, unit in enumerate(household["tax_units"]):
            people = [
                dict(p, interest=0.0) if t % 2 else dict(p) for p in unit["people"]
            ]
            units.append(dict(unit, people=people))
        out.append(dict(household, tax_units=units))
    return out


def _check_locality(households, year):
    before = _calculate(households, year)["deduction"]
    after = _calculate(_zero_odd_units(households), year)["deduction"]
    unit_index = np.array(
        [t for household in households for t in range(len(household["tax_units"]))]
    )
    # 3. Even-numbered tax units kept their own loans and their deduction.
    even = unit_index % 2 == 0
    np.testing.assert_allclose(after[even], before[even], atol=TOLERANCE)


def test_seeded_mixed_batch_2025():
    households = _seeded_households()
    result = _check(households, "2025")
    # The two tie households at the end: the first listed tax unit holds it.
    assert result["interest"][-4:].tolist() == [5_000, 0, 5_000, 0]


def test_seeded_mixed_batch_2026_locality():
    households = _seeded_households(seed=20261024)
    _check(households, "2026")
    _check_locality(households, "2026")


def test_people_listed_out_of_household_order():
    # Microdata need not list a household's members next to each other.
    households = _seeded_households(n=60, seed=20261025, ties=False)
    _check(households, "2025", shuffle_seed=7)


@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(household_specs(), min_size=1, max_size=6),
    st.sampled_from(["2025", "2026", "2028"]),
)
def test_attribution_invariants(households, year):
    _check(households, year)
    _check_locality(households, year)
