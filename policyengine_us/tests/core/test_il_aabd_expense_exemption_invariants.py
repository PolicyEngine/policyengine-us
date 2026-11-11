"""Invariants for the Illinois AABD employment expense exemption.

89 Ill. Adm. Code 113.125(a) exempts withholding taxes and Social Security
tax as recognized expenses of employment, and IDHS PM 08-02-00 allows these
deductions "from the employed person's earned income". So each person's
exemption comes from their own wages only. The exemption's sources list used
to name the tax unit's state_withheld_income_tax, which policyengine-core
projects onto every member of the tax unit, so each member deducted the whole
unit's Illinois withholding. It now names the person's own
il_withheld_income_tax.

Hypothesis draws batches of Illinois tax units (single, joint, head of
household with dependents, joint with dependents), and a seeded population
of 200 units adds breadth. Each batch runs as one vectorized simulation, and
again with every head's wages raised by a drawn non-negative amount. For
every person, in January 2024 and January 2025:

1. Differential: il_aabd_expense_exemption_person equals an independent
   numpy sum of the person's own Illinois withholding estimate (4.95% of
   wages above the personal exemption) and their own 6.2% Social Security
   tax, per month. A tax unit dependent's withholding estimate is zero,
   because irs_gross_income leaves a dependent's income to their own return;
   their Social Security tax still counts.
2. Accounting: in each tax unit, the members' withholding parts sum to the
   unit's state_withheld_income_tax, so each member's withholding is counted
   once rather than once per member.
3. Non-interference: raising the head's wages changes no other member's
   exemption, or their AABD earned income after exemptions.
4. Monotone: raising the head's wages never lowers the head's exemption.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars a month

# Illinois flat rate (35 ILCS 5/201(b)) and personal exemption amount from the
# IL-1040 instructions for each tax year.
IL_RATE = 0.0495
IL_PERSONAL_EXEMPTION = {2024: 2_775, 2025: 2_850}
# Employee Social Security tax rate and contribution and benefit base.
SS_RATE = 0.062
SS_WAGE_BASE = {2024: 168_600, 2025: 176_100}
YEARS = sorted(IL_PERSONAL_EXEMPTION)
MONTHS = 12

# Zeros, wages around the personal exemption, and ordinary wages.
wages = st.one_of(
    st.just(0.0),
    st.integers(1, 3_000).map(float),
    st.integers(3_000, 150_000).map(float),
)
raises = st.one_of(st.just(0.0), st.integers(1, 20_000).map(float))


@st.composite
def people(draw):
    return {
        "employment_income": draw(wages),
        "is_disabled": draw(st.booleans()),
        "is_blind": draw(st.booleans()),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "hoh", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [
            {**draw(people()), "age": draw(st.sampled_from([10, 17, 25]))}
            for _ in range(n_dependents)
        ],
        "raise": draw(raises),
    }


SEED = 20261006


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def person():
        band = rng.choice([0, 1, 2])
        return {
            "employment_income": float(
                [0, rng.integers(1, 3_001), rng.integers(3_000, 150_001)][band]
            ),
            "is_disabled": bool(rng.random() < 0.5),
            "is_blind": bool(rng.random() < 0.2),
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "hoh", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [
                    {**person(), "age": int(rng.choice([10, 17, 25]))}
                    for _ in range(n_dependents)
                ],
                "raise": float(rng.integers(0, 20_001)) if rng.random() < 0.7 else 0.0,
            }
        )
    return units


def _situation(units, year, *, raise_heads):
    people = {}
    groups = {
        name: {}
        for name in [
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        ]
    }

    def add(name, values, role, extra_wages=0.0):
        people[name] = {
            "age": {"head": 45, "spouse": 43}.get(role, values.get("age")),
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "employment_income": values["employment_income"] + extra_wages,
            "is_disabled": values["is_disabled"],
            "is_blind": values["is_blind"],
            # Keep SSI, and so AABD unearned income, at zero.
            "takes_up_ssi_if_eligible": False,
        }

    for i, unit in enumerate(units):
        head = f"head_{i}"
        add(head, unit["head"], "head", raise_heads * unit["raise"])
        members, couple = [head], [head]
        if unit["spouse"] is not None:
            spouse = f"spouse_{i}"
            add(spouse, unit["spouse"], "spouse")
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, dependent in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            add(name, dependent, "dependent")
            members.append(name)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [name]}
        for group in ["tax_units", "spm_units", "families"]:
            groups[group][f"{group}_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "IL"},
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, raise_heads=False):
    sim = Simulation(situation=_situation(units, year, raise_heads=raise_heads))
    month = f"{year}-01"
    out = {
        name: np.asarray(sim.calculate(name, month), dtype=float)
        for name in [
            "il_aabd_expense_exemption_person",
            "il_aabd_child_care_expense_exemption",
            "il_aabd_earned_income_after_exemption_person",
            "il_withheld_income_tax",
            "employee_social_security_tax",
            "state_withheld_income_tax",
        ]
    }
    out["wages"] = np.asarray(sim.calculate("employment_income", year), dtype=float)
    out["head"] = np.asarray(sim.calculate("is_tax_unit_head", year))
    out["dependent"] = np.asarray(sim.calculate("is_tax_unit_dependent", year))
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"],
        weights=values,
        minlength=len(run["state_withheld_income_tax"]),
    )


def _check(units, year):
    base = _run(units, year)
    exemption = base["il_aabd_expense_exemption_person"]

    # 1. Differential against numpy.
    wages = base["wages"]
    own_withholding = np.where(
        base["dependent"],
        0,
        IL_RATE * np.maximum(wages - IL_PERSONAL_EXEMPTION[year], 0),
    )
    own_ss_tax = SS_RATE * np.minimum(wages, SS_WAGE_BASE[year])
    np.testing.assert_allclose(
        base["il_withheld_income_tax"], own_withholding / MONTHS, atol=TOLERANCE
    )
    np.testing.assert_allclose(
        base["employee_social_security_tax"], own_ss_tax / MONTHS, atol=TOLERANCE
    )
    np.testing.assert_allclose(
        exemption,
        (own_withholding + own_ss_tax) / MONTHS
        + base["il_aabd_child_care_expense_exemption"],
        atol=TOLERANCE,
    )

    # 2. Each member's withholding is counted once per tax unit.
    withholding_part = (
        exemption
        - base["employee_social_security_tax"]
        - base["il_aabd_child_care_expense_exemption"]
    )
    np.testing.assert_allclose(
        _unit_sum(base, withholding_part),
        base["state_withheld_income_tax"],
        atol=TOLERANCE,
    )

    # 3. and 4. Raise only the heads' wages.
    raised = _run(units, year, raise_heads=True)
    others = ~base["head"]
    for name in [
        "il_aabd_expense_exemption_person",
        "il_aabd_earned_income_after_exemption_person",
    ]:
        np.testing.assert_allclose(
            raised[name][others], base[name][others], atol=TOLERANCE, err_msg=name
        )
    head = base["head"]
    assert (
        raised["il_aabd_expense_exemption_person"][head] >= exemption[head] - TOLERANCE
    ).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_il_aabd_expense_exemption_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
