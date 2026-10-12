"""Invariants for the 2020 unemployment compensation exclusion, IRC 85(c).

IRC 85(c)(1): for a taxable year beginning in 2020, a taxpayer whose adjusted
gross income is less than $150,000 excludes up to $10,200 of the unemployment
compensation they received, "or, in the case of a joint return, received by
each spouse". IRC 85(c)(2): that adjusted gross income is figured after
section 86 and without regard to section 85, so without any unemployment
compensation (2020 Unemployment Compensation Exclusion Worksheet, line 6).
A dependent's compensation is on the dependent's own return.

Hypothesis draws batches of tax units (single, joint, joint with a child or
student dependent, single parent) with income near the $150,000 cutoff. Each
drawn unit appears three times in one vectorized 2020 simulation: as drawn,
with its dependents' compensation set to zero, and with the head's and
spouse's compensation swapped. A 2021 simulation of the drawn units checks
that the exclusion ends. For every person and tax unit:

1. Bounds: the exempt part of each person's compensation is between zero and
   the lesser of what they received and $10,200, and zero in 2021.
2. Cutoff: the head's and spouse's compensation is exempt only when the tax
   unit's `taxable_uc_agi` is under $150,000, a dependent's only when their
   own `dependent_taxable_uc_agi` is, and then each person's exempt part is
   the lesser of their own compensation and $10,200.
3. Differential: `taxable_uc_agi` equals adjusted gross income less the
   taxable compensation on the return, floored at zero. The model figures
   AGI without the compensation once from gross income sources and once,
   here, from AGI itself; the two must agree, so the compensation is left
   out exactly once.
4. Return boundary: the tax unit's taxable compensation is the sum over its
   head and spouse, and dependents' compensation never changes the filers'
   taxable compensation, `taxable_uc_agi` or AGI.
5. Symmetry: swapping the head's and spouse's compensation swaps their
   taxable compensation and leaves the return's total unchanged.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

CUTOFF = 150_000
AMOUNT = 10_200
TOLERANCE = dict(rtol=1e-6, atol=0.01)

PERSON_OUTPUTS = [
    "unemployment_compensation",
    "taxable_unemployment_compensation",
    "tax_exempt_unemployment_compensation",
    "is_tax_unit_dependent",
    "dependent_taxable_uc_agi",
]
TAX_UNIT_OUTPUTS = [
    "taxable_uc_agi",
    "tax_unit_taxable_unemployment_compensation",
    "adjusted_gross_income",
]
VARIANTS = ["drawn", "no_dependent_uc", "swapped"]

# Amounts that land on and around the cutoff and the exclusion cap.
money = st.one_of(
    st.just(0),
    st.integers(1, 200_000),
    st.sampled_from([CUTOFF - 1, CUTOFF, CUTOFF + 1]),
)
compensation = st.one_of(
    st.just(0),
    st.integers(1, 30_000),
    st.sampled_from([AMOUNT - 1, AMOUNT, AMOUNT + 1]),
)


@st.composite
def adults(draw):
    age = draw(st.integers(25, 80))
    return {
        "age": age,
        "employment_income": draw(money),
        "taxable_pension_income": draw(st.sampled_from([0, 20_000, 140_000])),
        "social_security_retirement": draw(st.sampled_from([0, 20_000]))
        if age >= 62
        else 0,
        "early_withdrawal_penalty": draw(st.sampled_from([0, 500])),
        "unemployment_compensation": draw(compensation),
    }


@st.composite
def dependents(draw, students_allowed):
    # Qualifying children: their income never decides whether they are
    # dependents, so zeroing their compensation keeps the tax unit's shape.
    student = students_allowed and draw(st.booleans())
    return {
        "age": draw(st.integers(19, 23)) if student else draw(st.integers(0, 17)),
        "is_full_time_student": student,
        "employment_income": draw(st.sampled_from([0, 8_000])),
        "dividend_income": draw(st.sampled_from([0, 160_000])),
        "unemployment_compensation": draw(compensation),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "joint_child", "parent"]))
    head = draw(adults())
    spouse = draw(adults()) if kind.startswith("joint") else None
    # A single parent's adult student would be taken for a spouse.
    children = (
        [draw(dependents(students_allowed=kind == "joint_child"))]
        if kind in ("joint_child", "parent")
        else []
    )
    return {"head": head, "spouse": spouse, "children": children}


def _variant(unit, variant):
    adults_ = [dict(unit["head"])] + ([dict(unit["spouse"])] if unit["spouse"] else [])
    children = [dict(child) for child in unit["children"]]
    if variant == "no_dependent_uc":
        for child in children:
            child["unemployment_compensation"] = 0
    if variant == "swapped" and len(adults_) == 2:
        first, second = adults_
        first["unemployment_compensation"], second["unemployment_compensation"] = (
            second["unemployment_compensation"],
            first["unemployment_compensation"],
        )
    return adults_, children


def _situation(units, year, variants):
    """Each variant holds every drawn unit, in the same order, so a person's
    position within a variant is the same in all of them."""
    people, tax_units_, marital_units, households = {}, {}, {}, {}
    for variant in variants:
        for i, unit in enumerate(units):
            adults_, children = _variant(unit, variant)
            key = f"{variant}_{i}"
            adult_names = [f"{key}_adult{j}" for j in range(len(adults_))]
            child_names = [f"{key}_child{j}" for j in range(len(children))]
            for name, inputs in zip(adult_names + child_names, adults_ + children):
                people[name] = {k: {year: v} for k, v in inputs.items()}
            members = adult_names + child_names
            tax_units_[key] = {"members": members}
            marital_units[key] = {"members": adult_names}
            for name in child_names:
                marital_units[name] = {"members": [name]}
            households[key] = {"members": members, "state_code": {year: "TX"}}
    return {
        "people": people,
        "tax_units": tax_units_,
        "marital_units": marital_units,
        "households": households,
    }


def _couples(units):
    """Positions, within a variant, of each joint unit's two adults."""
    pairs, position = [], 0
    for unit in units:
        if unit["spouse"]:
            pairs.append((position, position + 1))
        position += 1 + bool(unit["spouse"]) + len(unit["children"])
    return np.array(pairs, dtype=int).reshape(-1, 2), position


def _run(units, year, variants):
    sim = Simulation(situation=_situation(units, year, variants))
    run = {
        name: np.asarray(sim.calculate(name, year))
        for name in PERSON_OUTPUTS + TAX_UNIT_OUTPUTS
    }
    run["tax_unit_index"] = sim.populations["tax_unit"].members_entity_id
    return run


def _check_2020(units):
    run = _run(units, 2020, VARIANTS)
    received = run["unemployment_compensation"]
    exempt = run["tax_exempt_unemployment_compensation"]
    taxable = run["taxable_unemployment_compensation"]
    dependent = run["is_tax_unit_dependent"]
    filer = ~dependent
    magi = run["taxable_uc_agi"]

    # 1. Bounds.
    cap = np.minimum(np.maximum(received, 0), AMOUNT)
    assert (exempt >= -TOLERANCE["atol"]).all()
    assert (exempt <= cap + TOLERANCE["atol"]).all()
    np.testing.assert_allclose(taxable + exempt, received, **TOLERANCE)

    # 2. Cutoff: the filers' return, and each dependent's own return.
    filer_under = magi[run["tax_unit_index"]] < CUTOFF
    dependent_under = run["dependent_taxable_uc_agi"] < CUTOFF
    under = np.where(dependent, dependent_under, filer_under)
    np.testing.assert_allclose(exempt, under * cap, **TOLERANCE)

    # 3. Differential: AGI without the compensation, two ways.
    np.testing.assert_allclose(
        magi,
        np.maximum(
            0,
            run["adjusted_gross_income"]
            - run["tax_unit_taxable_unemployment_compensation"],
        ),
        **TOLERANCE,
    )

    # 4. Return boundary: the return sums the filers only, and dependents'
    # compensation changes nothing on it.
    np.testing.assert_allclose(
        run["tax_unit_taxable_unemployment_compensation"],
        np.bincount(
            run["tax_unit_index"], weights=taxable * filer, minlength=len(magi)
        ),
        **TOLERANCE,
    )
    pairs, people_per_variant = _couples(units)
    n = len(units)
    drawn, no_dependent_uc, swapped = (
        slice(k * n, (k + 1) * n) for k in range(len(VARIANTS))
    )
    for name in TAX_UNIT_OUTPUTS:
        np.testing.assert_allclose(
            run[name][no_dependent_uc], run[name][drawn], err_msg=name, **TOLERANCE
        )
    people = [
        slice(k * people_per_variant, (k + 1) * people_per_variant)
        for k in range(len(VARIANTS))
    ]
    drawn_filer = filer[people[0]]
    np.testing.assert_allclose(
        taxable[people[1]][drawn_filer], taxable[people[0]][drawn_filer], **TOLERANCE
    )

    # 5. Symmetry between spouses.
    np.testing.assert_allclose(
        run["tax_unit_taxable_unemployment_compensation"][swapped],
        run["tax_unit_taxable_unemployment_compensation"][drawn],
        **TOLERANCE,
    )
    if len(pairs):
        for k in (0, 1):
            # The swapped variant's adult k received the other adult's
            # compensation, so is taxed on it as the other adult was.
            np.testing.assert_allclose(
                received[people[2]][pairs[:, k]], received[people[0]][pairs[:, 1 - k]]
            )
            np.testing.assert_allclose(
                taxable[people[2]][pairs[:, k]],
                taxable[people[0]][pairs[:, 1 - k]],
                **TOLERANCE,
            )


def _check_2021(units):
    run = _run(units, 2021, ["drawn"])
    np.testing.assert_allclose(run["tax_exempt_unemployment_compensation"], 0)
    np.testing.assert_allclose(
        run["taxable_unemployment_compensation"],
        run["unemployment_compensation"],
        **TOLERANCE,
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=30))
def test_exclusion_invariants_2020(units):
    _check_2020(units)


@settings(**dict(SETTINGS, max_examples=2))
@given(st.lists(tax_units(), min_size=10, max_size=30))
def test_exclusion_ends_after_2020(units):
    _check_2021(units)
