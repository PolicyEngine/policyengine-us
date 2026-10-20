"""New Mexico child income tax credit children and the 65+ medical exemption.

NMSA 7-2-18.34(J)(2) defines the child income tax credit's "qualifying child"
by IRC 152(c), which has no taxpayer identification number requirement, so
`nm_ctc_qualifying_children` counts 152(c) children whatever their Social
Security number status. NMSA 7-2-5.9 gives $3,000 to a filer or spouse 65 or
older with at least $28,000 of medical care expenses (the PIT-ADJ reading of
the threshold), with no halving for married filing separately.

For households drawn by Hypothesis and a seeded population, in 2023-2026:

1. Reference count: `nm_ctc_qualifying_children` equals an independent count
   of the 152(c) tests the model records: a dependent who is the filer's
   child (not a parent or grandparent) and is either permanently and totally
   disabled, or younger than the older filer and under 19 or a full-time
   student under 24. Outside New Mexico it is 0.
2. Superset: where every dependent is younger than the older filer, it is
   never below the federal `eitc_child_count`, which adds the Social Security
   number requirement. (The federal helper does not apply the relative-age
   test of IRC 152(c)(3)(A), so the two counts are not ordered otherwise.)
3. Identification invariance: giving every dependent a Social Security
   number changes neither the count nor `nm_ctc`.
4. Label invariance: exchanging the head and spouse labels changes neither
   the count, `nm_ctc` nor `nm_medical_expense_exemption`.
5. Separate filing: a single adult filing separately gets half of `nm_ctc`
   (7-2-18.34(G)) and the whole `nm_medical_expense_exemption`.
6. Reference exemption: `nm_medical_expense_exemption` is $3,000 exactly when
   a filer (not a dependent) is 65 or older and medical expenses are at least
   $28,000, and 0 otherwise.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = [2023, 2024, 2025, 2026]
STATES = ["NM", "NM", "NM", "TX"]
SSN_CARD_TYPES = ["CITIZEN", "NON_CITIZEN_VALID_EAD", "OTHER_NON_CITIZEN", "NONE"]
RELATIONS = ["child", "child", "child", "parent", "grandparent"]
EXEMPTION = 3_000
MIN_EXPENSES = 28_000
TOLERANCE = 0.01
# Each drawn unit is computed four times: as drawn; with every dependent
# given a Social Security number; with the head and spouse labels exchanged;
# and filing separately (a single adult only).
DRAWN, CITIZEN, SWAPPED, SEPARATE = range(4)


def money(high):
    return st.one_of(st.just(0), st.integers(1, high))


@st.composite
def adults(draw):
    return {
        "age": draw(st.integers(18, 90)),
        "employment_income": draw(money(120_000)),
        "claimed_as_dependent_on_another_return": draw(st.booleans()),
    }


@st.composite
def dependents(draw):
    relation = draw(st.sampled_from(RELATIONS))
    if relation == "child":
        age = draw(st.integers(0, 30))
    else:
        age = draw(st.integers(40, 95))
    return {
        "relation": relation,
        "age": age,
        "is_full_time_student": draw(st.booleans()) if 18 <= age <= 25 else False,
        "is_permanently_and_totally_disabled": draw(
            st.booleans() if relation == "child" else st.just(False)
        ),
        "ssn_card_type": draw(st.sampled_from(SSN_CARD_TYPES)),
    }


@st.composite
def units(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": draw(st.lists(adults(), min_size=1, max_size=2)),
        "dependents": draw(st.lists(dependents(), max_size=3)),
        "medical_expenses": draw(
            st.one_of(
                st.sampled_from([27_999, 28_000, 28_001]),
                money(60_000),
            )
        ),
    }


def _seeded_units(n, seed=20261009):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        drawn_adults = []
        for _ in range(int(rng.integers(1, 3))):
            drawn_adults.append(
                {
                    "age": int(rng.integers(18, 91)),
                    "employment_income": float(round(rng.uniform(0, 120_000))),
                    "claimed_as_dependent_on_another_return": bool(rng.random() < 0.2),
                }
            )
        drawn_dependents = []
        for _ in range(int(rng.integers(0, 4))):
            relation = RELATIONS[int(rng.integers(len(RELATIONS)))]
            age = int(
                rng.integers(0, 31) if relation == "child" else rng.integers(40, 96)
            )
            drawn_dependents.append(
                {
                    "relation": relation,
                    "age": age,
                    "is_full_time_student": bool(
                        18 <= age <= 25 and rng.random() < 0.5
                    ),
                    "is_permanently_and_totally_disabled": bool(
                        relation == "child" and rng.random() < 0.1
                    ),
                    "ssn_card_type": SSN_CARD_TYPES[
                        int(rng.integers(len(SSN_CARD_TYPES)))
                    ],
                }
            )
        out.append(
            {
                "state": STATES[i % len(STATES)],
                "adults": drawn_adults,
                "dependents": drawn_dependents,
                "medical_expenses": float(
                    [27_999, 28_000, 28_001][i % 3]
                    if i % 4 == 0
                    else round(rng.uniform(0, 60_000))
                ),
            }
        )
    return out


def _crafted_units():
    """Edge cases the seeded draw rarely reaches."""

    def adult(age, income=20_000.0):
        return {
            "age": age,
            "employment_income": income,
            "claimed_as_dependent_on_another_return": False,
        }

    def dependent(age, student=False, disabled=False, ssn="OTHER_NON_CITIZEN"):
        return {
            "relation": "child",
            "age": age,
            "is_full_time_student": student,
            "is_permanently_and_totally_disabled": disabled,
            "ssn_card_type": ssn,
        }

    def unit(adults, dependents, expenses=0.0):
        return {
            "state": "NM",
            "adults": adults,
            "dependents": dependents,
            "medical_expenses": expenses,
        }

    elderly_parent = {**dependent(70, ssn="CITIZEN"), "relation": "parent"}
    return [
        # A student sibling older than, or as old as, the filer.
        unit([adult(20)], [dependent(22, student=True)]),
        unit([adult(20)], [dependent(20, student=True)]),
        # A disabled sibling older than the filer.
        unit([adult(20)], [dependent(30, disabled=True)]),
        # Younger than the older spouse only.
        unit([adult(25), adult(20)], [dependent(22, student=True)]),
        # The only 65+ person is a dependent parent.
        unit([adult(40)], [elderly_parent], expenses=30_000.0),
        # A 65+ filer with exactly $28,000 of expenses.
        unit([adult(70)], [], expenses=28_000.0),
    ]


def _situation(drawn_units, year):
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(drawn_units):
        for copy in (DRAWN, CITIZEN, SWAPPED, SEPARATE):
            members = []
            adult_list = list(unit["adults"])
            if copy == SWAPPED:
                adult_list = adult_list[::-1]
            for j, adult in enumerate(adult_list):
                name = f"adult_{i}_{copy}_{j}"
                people[name] = {
                    "age": adult["age"],
                    "employment_income": adult["employment_income"],
                    "claimed_as_dependent_on_another_return": adult[
                        "claimed_as_dependent_on_another_return"
                    ],
                    "is_tax_unit_head": j == 0,
                    "is_tax_unit_spouse": j == 1,
                    "is_tax_unit_dependent": False,
                    "medicare_enrolled": False,
                }
                members.append(name)
            people[members[0]]["other_medical_expenses"] = unit["medical_expenses"]
            for j, dependent in enumerate(unit["dependents"]):
                name = f"dependent_{i}_{copy}_{j}"
                people[name] = {
                    "age": dependent["age"],
                    "is_full_time_student": dependent["is_full_time_student"],
                    "is_permanently_and_totally_disabled": dependent[
                        "is_permanently_and_totally_disabled"
                    ],
                    "is_parent_of_filer_or_spouse": dependent["relation"] == "parent",
                    "is_grandparent_of_filer_or_spouse": dependent["relation"]
                    == "grandparent",
                    "ssn_card_type": (
                        "CITIZEN" if copy == CITIZEN else dependent["ssn_card_type"]
                    ),
                    "is_tax_unit_head": False,
                    "is_tax_unit_spouse": False,
                    "is_tax_unit_dependent": True,
                    "medicare_enrolled": False,
                }
                members.append(name)
            tax_unit = {"members": members}
            if len(unit["adults"]) == 2:
                tax_unit["filing_status"] = {year: "JOINT"}
            elif copy == SEPARATE:
                tax_unit["filing_status"] = {year: "SEPARATE"}
            tax_units[f"tax_unit_{i}_{copy}"] = tax_unit
            households[f"household_{i}_{copy}"] = {
                "members": members,
                "state_code": {year: unit["state"]},
            }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, "tax_units": tax_units, "households": households}


def _reference_children(unit):
    if unit["state"] != "NM":
        return 0
    oldest_filer = max(a["age"] for a in unit["adults"])
    return sum(
        d["relation"] == "child"
        and (
            d["is_permanently_and_totally_disabled"]
            or (
                d["age"] < oldest_filer
                and (d["age"] < 19 or (d["is_full_time_student"] and d["age"] < 24))
            )
        )
        for d in unit["dependents"]
    )


def _reference_exemption(unit):
    if unit["state"] != "NM":
        return 0
    filer_65 = any(a["age"] >= 65 for a in unit["adults"])
    return EXEMPTION * (filer_65 and unit["medical_expenses"] >= MIN_EXPENSES)


def _describe(unit):
    return (
        f"{unit['state']} adults={[(a['age'], a['claimed_as_dependent_on_another_return']) for a in unit['adults']]} "
        f"dependents={[(d['relation'], d['age'], d['ssn_card_type']) for d in unit['dependents']]} "
        f"expenses={unit['medical_expenses']}"
    )


def check_invariants(drawn_units, year):
    sim = Simulation(situation=_situation(drawn_units, year))

    def calc(name):
        return np.asarray(sim.calculate(name, year), dtype=float).reshape(-1, 4)

    children = calc("nm_ctc_qualifying_children")
    eitc_children = calc("eitc_child_count")
    credit = calc("nm_ctc")
    exemption = calc("nm_medical_expense_exemption")
    for i, unit in enumerate(drawn_units):
        where = f"{year} unit {i}: {_describe(unit)}"
        single = len(unit["adults"]) == 1
        # 1. Reference count.
        assert children[i, DRAWN] == _reference_children(unit), where
        # 2. Superset of the EITC count where every dependent is younger than
        # the older filer (the New Mexico count is 0 elsewhere).
        oldest_filer = max(a["age"] for a in unit["adults"])
        if unit["state"] == "NM" and all(
            d["age"] < oldest_filer for d in unit["dependents"]
        ):
            assert children[i, DRAWN] >= eitc_children[i, DRAWN], where
        # 3. Identification invariance.
        assert children[i, CITIZEN] == children[i, DRAWN], where
        assert abs(credit[i, CITIZEN] - credit[i, DRAWN]) <= TOLERANCE, where
        # 4. Label invariance.
        assert children[i, SWAPPED] == children[i, DRAWN], where
        assert abs(credit[i, SWAPPED] - credit[i, DRAWN]) <= TOLERANCE, where
        assert abs(exemption[i, SWAPPED] - exemption[i, DRAWN]) <= TOLERANCE, where
        # 5. Separate filing.
        if single:
            assert abs(credit[i, SEPARATE] - credit[i, DRAWN] / 2) <= TOLERANCE, where
            assert abs(exemption[i, SEPARATE] - exemption[i, DRAWN]) <= TOLERANCE, where
        # 6. Reference exemption.
        assert abs(exemption[i, DRAWN] - _reference_exemption(unit)) <= TOLERANCE, where
    return credit[:, DRAWN], exemption[:, DRAWN]


def _assert_coverage(drawn_units, credit, exemption):
    """The seeded population reaches the cases the invariants are about."""
    single = np.array([len(u["adults"]) == 1 for u in drawn_units])
    child_without_ssn = np.array(
        [
            any(
                d["relation"] == "child"
                and d["age"] < 19
                and d["ssn_card_type"] in ("OTHER_NON_CITIZEN", "NONE")
                for d in u["dependents"]
            )
            for u in drawn_units
        ]
    )
    elderly_dependent_only = np.array(
        [
            u["state"] == "NM"
            and all(a["age"] < 65 for a in u["adults"])
            and any(d["age"] >= 65 for d in u["dependents"])
            and u["medical_expenses"] >= MIN_EXPENSES
            for u in drawn_units
        ]
    )
    not_younger_than_filers = np.array(
        [
            any(
                d["relation"] == "child"
                and not d["is_permanently_and_totally_disabled"]
                and d["age"] >= max(a["age"] for a in u["adults"])
                and (d["age"] < 19 or (d["is_full_time_student"] and d["age"] < 24))
                for d in u["dependents"]
            )
            for u in drawn_units
        ]
    )
    assert (child_without_ssn & (credit > 0)).any()
    assert not_younger_than_filers.any()
    assert (single & (credit > 0)).any()
    assert (single & (exemption > 0)).any()
    assert elderly_dependent_only.any()


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(units(), min_size=8, max_size=20))
def test_nm_ctc_children_and_medical_exemption_hypothesis(year, drawn_units):
    check_invariants(drawn_units, year)


@pytest.mark.parametrize("year", YEARS)
def test_nm_ctc_children_and_medical_exemption_seeded_population(year):
    drawn_units = _seeded_units(40) + _crafted_units()
    credit, exemption = check_invariants(drawn_units, year)
    _assert_coverage(drawn_units, credit, exemption)
