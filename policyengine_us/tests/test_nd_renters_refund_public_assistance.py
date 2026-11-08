"""Invariants for public assistance in North Dakota's renter's refund income.

N.D.C.C. 57-02-08.1(5)(c) (https://ndlegis.gov/cencode/t57c02.pdf#page=16)
counts income "including any county, state, or federal public assistance
benefits" and excludes "any amount excluded from income by federal or state
law". No federal or North Dakota law excludes SSI, TANF or general assistance
from income. 7 U.S.C. 2017(b) excludes SNAP from income "for any purpose under
any Federal, State, or local laws", and 42 U.S.C. 8624(f)(1) excludes LIHEAP,
including North Dakota's, "for any purpose under any Federal or State law".
SSI and general assistance belong to a person; TANF belongs to an SPM unit,
and add() gives each member of the unit an equal share, which counts in that
member's tax unit.

Four invariants hold for every input.

1. A dollar of a tax unit's SSI, general assistance or TANF share raises its
   renter's refund income by at most a dollar and never lowers it. It raises
   it by exactly a dollar when the income without the benefits exceeds zero,
   since only the floor at zero can absorb any of it.
2. SNAP and North Dakota LIHEAP never change renter's refund income or the
   refund.
3. Public assistance never raises the refund, since the refund falls as
   income rises.
4. TANF counts once in total across the tax units of an SPM unit: the shares
   the tax units count sum to the unit's benefit, each in proportion to the
   tax unit's members. This per-person split is the model's attribution of an
   SPM unit's benefit, which this test pins.

YAML pins one household per case. These need random amounts, medical costs
that push income to the floor, and SPM units that hold more than one tax unit.
"""

from collections import Counter

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
# Amounts are float32 in the model.
TOLERANCE = 0.5


@st.composite
def spm_units(draw, positive_income=False):
    """A renter aged 65 or more in their own tax unit, sometimes sharing the
    SPM unit with a parent and child in a second tax unit."""
    wages = st.integers(min_value=1 if positive_income else 0, max_value=40_000)
    benefit = st.integers(min_value=0, max_value=12_000)
    unit = {
        "renter": {
            "age": draw(st.integers(min_value=65, max_value=90)),
            "employment_income": draw(wages),
            "ssi": draw(benefit),
            "general_assistance": draw(benefit),
            # Medical costs above income push income to the zero floor.
            "other_medical_expenses": (
                0 if positive_income else draw(st.integers(0, 60_000))
            ),
            "rent": draw(st.integers(min_value=0, max_value=15_000)),
        },
        "tanf": draw(st.integers(min_value=0, max_value=10_000)),
        "snap": draw(st.integers(min_value=0, max_value=8_000)),
        "nd_liheap": draw(st.integers(min_value=0, max_value=3_000)),
    }
    if positive_income or draw(st.booleans()):
        unit["family"] = {
            "parent_wages": draw(wages),
            "child_ssi": draw(benefit),
        }
    return unit


def without_public_assistance(unit):
    renter = {**unit["renter"], "ssi": 0, "general_assistance": 0}
    family = unit.get("family")
    if family is not None:
        family = {**family, "child_ssi": 0}
    return {**unit, "renter": renter, "family": family, "tanf": 0}


def without(unit, *benefits):
    return {**unit, **{benefit: 0 for benefit in benefits}}


def situation(units):
    """One household, family and SPM unit per unit, all in North Dakota.
    Every benefit is an input, so no formula adds any other."""
    people, tax_units, marital_units = {}, {}, {}
    spm, families, households = {}, {}, {}
    for index, unit in enumerate(units):
        renter = f"renter_{index}"
        people[renter] = {
            "age": {YEAR: unit["renter"]["age"]},
            # No computed Medicare premium adds to the medical costs.
            "medicare_enrolled": {YEAR: False},
            "is_tax_unit_head": {YEAR: True},
            "is_tax_unit_dependent": {YEAR: False},
            **{
                name: {YEAR: unit["renter"][name]}
                for name in (
                    "employment_income",
                    "ssi",
                    "general_assistance",
                    "other_medical_expenses",
                    "rent",
                )
            },
        }
        members = [renter]
        tax_units[f"renter_tax_unit_{index}"] = {"members": [renter]}
        marital_units[f"renter_marital_unit_{index}"] = {"members": [renter]}
        family = unit.get("family")
        if family is not None:
            parent, child = f"parent_{index}", f"child_{index}"
            people[parent] = {
                "age": {YEAR: 30},
                "medicare_enrolled": {YEAR: False},
                "is_tax_unit_head": {YEAR: True},
                "is_tax_unit_dependent": {YEAR: False},
                "employment_income": {YEAR: family["parent_wages"]},
                "ssi": {YEAR: 0},
                "general_assistance": {YEAR: 0},
            }
            people[child] = {
                "age": {YEAR: 8},
                "medicare_enrolled": {YEAR: False},
                "is_tax_unit_head": {YEAR: False},
                "is_tax_unit_dependent": {YEAR: True},
                "ssi": {YEAR: family["child_ssi"]},
                "general_assistance": {YEAR: 0},
            }
            members += [parent, child]
            tax_units[f"family_tax_unit_{index}"] = {"members": [parent, child]}
            marital_units[f"parent_marital_unit_{index}"] = {"members": [parent]}
            marital_units[f"child_marital_unit_{index}"] = {"members": [child]}
        spm[f"spm_unit_{index}"] = {
            "members": members,
            "tanf": {YEAR: unit["tanf"]},
            "snap": {YEAR: unit["snap"]},
            "nd_liheap": {YEAR: unit["nd_liheap"]},
        }
        # Without explicit families, the model puts every person in one.
        families[f"family_{index}"] = {"members": members}
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {YEAR: "ND"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm,
        "families": families,
        "households": households,
    }


def tax_unit_rows(units):
    """For each tax unit in situation order: its SPM unit's index, its member
    count, and the SSI and general assistance its members receive."""
    rows = []
    for index, unit in enumerate(units):
        renter = unit["renter"]
        rows.append((index, 1, renter["ssi"] + renter["general_assistance"]))
        family = unit.get("family")
        if family is not None:
            rows.append((index, 2, family["child_ssi"]))
    return rows


def calculate(simulation, *names):
    return [simulation.calculate(name, YEAR).astype(float) for name in names]


def tanf_shares(units):
    """Each tax unit's members' equal shares of their SPM unit's TANF."""
    rows = tax_unit_rows(units)
    sizes = Counter()
    for index, members, _ in rows:
        sizes[index] += members
    return np.array(
        [units[index]["tanf"] * members / sizes[index] for index, members, _ in rows]
    )


def expected_public_assistance(units):
    """Each tax unit's SSI and general assistance, plus its TANF share."""
    person_benefits = np.array([benefits for _, _, benefits in tax_unit_rows(units)])
    return person_benefits + tanf_shares(units)


@settings(max_examples=12, deadline=None)
@given(units=st.lists(spm_units(), min_size=1, max_size=8))
@example(
    units=[
        # The renter's medical costs exceed wages and benefits together, so
        # the floor absorbs all of them.
        {
            "renter": {
                "age": 70,
                "employment_income": 5_000,
                "ssi": 6_000,
                "general_assistance": 1_000,
                "other_medical_expenses": 30_000,
                "rent": 6_000,
            },
            "tanf": 0,
            "snap": 2_000,
            "nd_liheap": 600,
        },
        # The floor absorbs part of the SSI.
        {
            "renter": {
                "age": 70,
                "employment_income": 0,
                "ssi": 9_000,
                "general_assistance": 0,
                "other_medical_expenses": 4_000,
                "rent": 6_000,
            },
            "tanf": 0,
            "snap": 0,
            "nd_liheap": 0,
        },
    ]
)
@example(
    units=[
        # Above the floor in a shared SPM unit, the renter's tax unit counts
        # 3,000 of SSI, 500 of general assistance and a third of the TANF
        # (4,700), and the family's counts the child's 2,400 of SSI and two
        # thirds of the TANF (4,800).
        {
            "renter": {
                "age": 72,
                "employment_income": 12_000,
                "ssi": 3_000,
                "general_assistance": 500,
                "other_medical_expenses": 0,
                "rent": 7_200,
            },
            "tanf": 3_600,
            "snap": 1_500,
            "nd_liheap": 900,
            "family": {"parent_wages": 9_000, "child_ssi": 2_400},
        }
    ]
)
def test_public_assistance_counts_dollar_for_dollar_above_the_floor(units):
    stripped = [without_public_assistance(unit) for unit in units]
    no_snap_or_liheap = [without(unit, "snap", "nd_liheap") for unit in units]
    simulation = Simulation(situation=situation(units + stripped + no_snap_or_liheap))
    # The SNAP and LIHEAP inputs reach the model, so the guard below tests them.
    for name in ("snap", "nd_liheap"):
        (amounts,) = calculate(simulation, name)
        np.testing.assert_allclose(
            amounts[: len(units)], [unit[name] for unit in units], atol=TOLERANCE
        )
    income, refund = calculate(
        simulation, "nd_renters_refund_income", "nd_renters_refund"
    )
    count = len(income) // 3
    with_benefits, without_benefits, without_snap_or_liheap = (
        income[:count],
        income[count : 2 * count],
        income[2 * count :],
    )
    benefits = expected_public_assistance(units)
    added = with_benefits - without_benefits
    assert (added >= -TOLERANCE).all()
    assert (added <= benefits + TOLERANCE).all()
    above_floor = without_benefits > 0
    np.testing.assert_allclose(
        added[above_floor], benefits[above_floor], atol=TOLERANCE
    )
    # SNAP and LIHEAP stay out of income and the refund.
    np.testing.assert_allclose(without_snap_or_liheap, with_benefits, atol=TOLERANCE)
    np.testing.assert_allclose(refund[2 * count :], refund[:count], atol=TOLERANCE)
    # More income never raises the refund.
    assert (refund[:count] <= refund[count : 2 * count] + TOLERANCE).all()


@settings(max_examples=12, deadline=None)
@given(units=st.lists(spm_units(positive_income=True), min_size=1, max_size=8))
@example(
    units=[
        {
            "renter": {
                "age": 72,
                "employment_income": 12_000,
                "ssi": 0,
                "general_assistance": 0,
                "other_medical_expenses": 0,
                "rent": 7_200,
            },
            "tanf": 3_600,
            "snap": 0,
            "nd_liheap": 0,
            "family": {"parent_wages": 9_000, "child_ssi": 0},
        }
    ]
)
def test_tanf_counts_once_across_the_tax_units_of_an_spm_unit(units):
    no_tanf = [without(unit, "tanf") for unit in units]
    (income,) = calculate(
        Simulation(situation=situation(units + no_tanf)), "nd_renters_refund_income"
    )
    count = len(income) // 2
    added = income[:count] - income[count:]
    # Every tax unit has wages, so the floor absorbs no share.
    np.testing.assert_allclose(added, tanf_shares(units), atol=TOLERANCE)
    totals = Counter()
    for (index, _, _), share in zip(tax_unit_rows(units), added):
        totals[index] += share
    for index, total in totals.items():
        assert total == pytest.approx(units[index]["tanf"], abs=TOLERANCE)
