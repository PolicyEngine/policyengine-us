"""Property tests: 529 deductions belong to the contributor, and Ohio limits
them per beneficiary.

`investment_in_529_plan_indv` records the person who contributed, and every
state models the deduction or credit for the contributor (Ohio: "allowed to a
taxpayer who contributes", R.C. 5747.70(A); Delaware: "contributed by an
individual", 30 Del. C. 1106(b)(11)). A contribution recorded on a tax unit
dependent is the dependent's own, deducted on their own return. So:

1. For every tax unit in a state with a 529 deduction or credit, state income
   tax is the same as when its dependents have no 529 contributions or
   beneficiary counts, and investment_in_529_plan is the head's and spouse's
   contributions.

Ohio limits the head's and spouse's combined contributions to $4,000 for each
beneficiary, whether they file jointly or separately, and carries the excess
forward (R.C. 5747.70(A); 2025 IT 1040 line 37). With R_b the head's and
spouse's contributions for beneficiary b in the tax unit
(investment_in_529_plan_as_beneficiary), C_b the carryforward for b, T the
head's and spouse's contributions, and n their beneficiary counts:

2. When all of the filers' contributions are for beneficiaries in the tax unit
   (T = sum R_b), the deduction is sum min(R_b + C_b, 4000).
3. Without per-beneficiary amounts or carryforwards, the deduction is
   min(T, 4000 n), as if contributions were split evenly.
4. The deduction is between 0 and max(T, sum R_b) + sum C_b; it does not
   change when contributions move between the spouses, and it does not fall
   when a carryforward rises.
5. Each person's share (oh_529_plan_deduction_person) is non-negative, a
   dependent's is zero, and the shares add up to the deduction.

Missouri, Mississippi and New Jersey give each filer a share of the tax unit's
deduction:

6. Shares are non-negative, a dependent's is zero, and they add up to the tax
   unit's deduction.

Virginia is left out of 1: PolicyEngine/policyengine-us#9875 moves its
deduction to the owner of record and drops dependents' accounts.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01
OH_CAP = 4_000

STATES = [
    "AL",
    "AZ",
    "CO",
    "DE",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "ND",
    "NE",
    "NJ",
    "NM",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "UT",
    "VT",
    "WI",
    "WV",
]
SHARED_DEDUCTIONS = {
    "MO": "mo_529_deduction",
    "MS": "ms_529_deduction",
    "NJ": "nj_529_deduction",
}
UNIT_OUTPUTS = [
    "state_income_tax",
    "investment_in_529_plan",
    "oh_529_plan_deduction",
    "adjusted_gross_income",
]
PERSON_OUTPUTS = [
    "is_tax_unit_dependent",
    "oh_529_plan_deduction_person",
    *SHARED_DEDUCTIONS.values(),
]


def amount(low, high):
    return st.integers(low, high).map(float)


def maybe(draw, high):
    """Zero half the time, so units with and without each item appear."""
    return draw(st.one_of(st.just(0.0), amount(0, high)))


@st.composite
def tax_units(draw):
    state = draw(st.sampled_from(STATES))
    n_filers = draw(st.integers(1, 2))
    n_dependents = draw(st.integers(0, 3))
    filers = [
        {
            "age": draw(st.integers(25, 75)),
            "employment_income": draw(amount(0, 300_000)),
            "investment_in_529_plan_indv": maybe(draw, 20_000),
            "count_529_contribution_beneficiaries": draw(st.integers(0, 3)),
            "investment_in_529_plan_as_beneficiary": 0.0,
            "oh_529_plan_deduction_carryforward": 0.0,
        }
        for _ in range(n_filers)
    ]
    dependents = [
        {
            "age": draw(st.integers(1, 17)),
            # The dependent's own contributions and beneficiaries.
            "investment_in_529_plan_indv": maybe(draw, 5_000),
            "count_529_contribution_beneficiaries": draw(st.integers(0, 2)),
            # The filers' contributions for this dependent.
            "investment_in_529_plan_as_beneficiary": maybe(draw, 10_000),
            "oh_529_plan_deduction_carryforward": maybe(draw, 6_000),
        }
        for _ in range(n_dependents)
    ]
    return {"state": state, "filers": filers, "dependents": dependents}


def build_situation(units):
    """One tax unit per household: the head, an optional spouse and the
    dependents."""
    people, tax_units_out, marital_units, households = {}, {}, {}, {}
    for i, unit in enumerate(units):
        members = []
        for j, person in enumerate(unit["filers"] + unit["dependents"]):
            name = f"person_{i}_{j}"
            filer = j < len(unit["filers"])
            people[name] = {
                "is_tax_unit_head": {YEAR: j == 0},
                "is_tax_unit_spouse": {YEAR: j == 1 and filer},
                "is_tax_unit_dependent": {YEAR: not filer},
                **{key: {YEAR: value} for key, value in person.items()},
            }
            members.append(name)
            if not filer:
                marital_units[f"dependent_{i}_{j}"] = {"members": [name]}
        tax_units_out[f"tax_unit_{i}"] = {"members": members}
        marital_units[f"filers_{i}"] = {"members": members[: len(unit["filers"])]}
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: unit["state"]},
        }
    return {
        "people": people,
        "tax_units": tax_units_out,
        "marital_units": marital_units,
        "households": households,
    }


def calculate(units):
    simulation = Simulation(situation=build_situation(units))
    unit_results = {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in UNIT_OUTPUTS
    }
    unit_results["filing_status"] = (
        simulation.calculate("filing_status", YEAR).decode_to_str().astype(str)
    )
    person_results = {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in PERSON_OUTPUTS
    }
    p = simulation.tax_benefit_system.parameters(YEAR).gov.states
    return unit_results, person_results, p


def members(units):
    return [person for unit in units for person in unit["filers"] + unit["dependents"]]


def unit_index(units):
    return np.concatenate(
        [
            np.full(len(unit["filers"]) + len(unit["dependents"]), i)
            for i, unit in enumerate(units)
        ]
    )


def unit_sum(values, index, n):
    return np.bincount(index, weights=values, minlength=n)


def inputs(units, name):
    return np.array([person[name] for person in members(units)], dtype=float)


def without_dependent_contributions(unit):
    zero = {
        "investment_in_529_plan_indv": 0.0,
        "count_529_contribution_beneficiaries": 0,
    }
    return {**unit, "dependents": [{**d, **zero} for d in unit["dependents"]]}


def spouses_swapped(unit):
    """Move all of the filers' contributions to the head."""
    if len(unit["filers"]) < 2:
        return unit
    head, spouse = unit["filers"]
    total = head["investment_in_529_plan_indv"] + spouse["investment_in_529_plan_indv"]
    return {
        **unit,
        "filers": [
            {**head, "investment_in_529_plan_indv": total},
            {**spouse, "investment_in_529_plan_indv": 0.0},
        ],
    }


def more_carryforward(unit):
    return {
        **unit,
        "dependents": [
            {
                **d,
                "oh_529_plan_deduction_carryforward": d[
                    "oh_529_plan_deduction_carryforward"
                ]
                + 1_000,
            }
            for d in unit["dependents"]
        ],
    }


def check(units):
    n = len(units)
    variants = [
        units,
        [without_dependent_contributions(unit) for unit in units],
        [spouses_swapped(unit) for unit in units],
        [more_carryforward(unit) for unit in units],
    ]
    all_units = [unit for variant in variants for unit in variant]
    unit_results, person_results, p = calculate(all_units)
    index = unit_index(units)
    n_people = len(index)
    states = np.array([unit["state"] for unit in units])

    def unit_part(variable, k):
        return unit_results[variable][k * n : (k + 1) * n]

    people = {name: values[:n_people] for name, values in person_results.items()}
    dependent = people["is_tax_unit_dependent"].astype(bool)
    filer = ~dependent

    # 1. Dependents' own contributions never reach the filers' state tax.
    np.testing.assert_allclose(
        unit_part("state_income_tax", 0),
        unit_part("state_income_tax", 1),
        atol=TOLERANCE,
        err_msg="state_income_tax",
    )
    contributions = unit_sum(
        inputs(units, "investment_in_529_plan_indv") * filer, index, n
    )
    np.testing.assert_allclose(
        unit_part("investment_in_529_plan", 0), contributions, atol=TOLERANCE
    )

    # Ohio.
    is_oh = states == "OH"
    deduction = unit_part("oh_529_plan_deduction", 0)
    for_member = inputs(units, "investment_in_529_plan_as_beneficiary")
    carryforward = inputs(units, "oh_529_plan_deduction_carryforward")
    counted = unit_sum(
        inputs(units, "count_529_contribution_beneficiaries") * filer, index, n
    )
    per_beneficiary = unit_sum(np.minimum(for_member + carryforward, OH_CAP), index, n)
    for_members = unit_sum(for_member, index, n)
    carried = unit_sum(carryforward, index, n)

    # 2. All contributions for members: the statute's limit per beneficiary.
    all_for_members = is_oh & np.isclose(contributions, for_members)
    np.testing.assert_allclose(
        deduction[all_for_members],
        per_beneficiary[all_for_members],
        atol=TOLERANCE,
    )
    # 3. No per-beneficiary amounts: the even split.
    no_detail = is_oh & (for_members == 0) & (carried == 0)
    np.testing.assert_allclose(
        deduction[no_detail],
        np.minimum(contributions, OH_CAP * counted)[no_detail],
        atol=TOLERANCE,
    )
    # 4. Bounds, the spouses' split, and carryforwards.
    assert np.all(deduction[is_oh] >= -TOLERANCE)
    assert np.all(
        deduction[is_oh]
        <= (np.maximum(contributions, for_members) + carried)[is_oh] + TOLERANCE
    )
    np.testing.assert_allclose(
        unit_part("oh_529_plan_deduction", 2)[is_oh],
        deduction[is_oh],
        atol=TOLERANCE,
        err_msg="spouses' split",
    )
    assert np.all(
        unit_part("oh_529_plan_deduction", 3)[is_oh] >= deduction[is_oh] - TOLERANCE
    )
    # 5. Ohio shares.
    in_oh = is_oh[index]
    shares = people["oh_529_plan_deduction_person"]
    assert np.all(shares[in_oh] >= -TOLERANCE)
    assert np.all(shares[dependent & in_oh] == 0)
    np.testing.assert_allclose(
        unit_sum(shares, index, n)[is_oh], deduction[is_oh], atol=TOLERANCE
    )

    # 6. Missouri, Mississippi and New Jersey shares add up to the tax
    # unit's capped contributions.
    filing_status = unit_part("filing_status", 0)
    agi = unit_part("adjusted_gross_income", 0)
    nj = p.nj.tax.income.deductions.plan_529_contributions
    unit_deductions = {
        "MO": np.minimum(
            contributions,
            p.mo.tax.income.subtractions.plan_529_contributions.cap[filing_status],
        ),
        "MS": np.minimum(
            contributions,
            p.ms.tax.income.adjustments.plan_529_contributions.cap[filing_status],
        ),
        "NJ": (agi <= nj.income_limit) * np.minimum(contributions, nj.cap),
    }
    for state, variable in SHARED_DEDUCTIONS.items():
        in_state = (states == state)[index]
        shares = people[variable]
        assert np.all(shares[in_state] >= -TOLERANCE), variable
        assert np.all(shares[dependent & in_state] == 0), variable
        np.testing.assert_allclose(
            unit_sum(shares, index, n)[states == state],
            unit_deductions[state][states == state],
            atol=TOLERANCE,
            err_msg=variable,
        )


# A simulation's cost is mostly fixed, so each example is a batch of tax
# units and there are few examples.
@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=20, max_size=40))
def test_529_deductions_follow_the_contributor(units):
    check(units)


def test_reported_examples():
    """Ohio households from the per-beneficiary limit: $8,000 for one child
    and $100 for another; two spouses contributing for the same child; a
    carryforward; and a child's own contribution."""
    zero = {
        "employment_income": 0.0,
        "investment_in_529_plan_indv": 0.0,
        "count_529_contribution_beneficiaries": 0,
        "investment_in_529_plan_as_beneficiary": 0.0,
        "oh_529_plan_deduction_carryforward": 0.0,
    }
    parent = {**zero, "age": 40, "employment_income": 80_000.0}
    child = {**zero, "age": 10}
    units = [
        {
            "state": "OH",
            "filers": [
                {
                    **parent,
                    "investment_in_529_plan_indv": 8_100.0,
                    "count_529_contribution_beneficiaries": 2,
                }
            ],
            "dependents": [
                {**child, "investment_in_529_plan_as_beneficiary": 8_000.0},
                {**child, "investment_in_529_plan_as_beneficiary": 100.0},
            ],
        },
        {
            "state": "OH",
            "filers": [
                {
                    **parent,
                    "investment_in_529_plan_indv": 3_000.0,
                    "count_529_contribution_beneficiaries": 1,
                },
                {
                    **parent,
                    "investment_in_529_plan_indv": 3_000.0,
                    "count_529_contribution_beneficiaries": 1,
                },
            ],
            "dependents": [
                {**child, "investment_in_529_plan_as_beneficiary": 6_000.0},
            ],
        },
        {
            "state": "OH",
            "filers": [{**parent}],
            "dependents": [{**child, "oh_529_plan_deduction_carryforward": 5_000.0}],
        },
        {
            "state": "OH",
            "filers": [{**parent}],
            "dependents": [
                {
                    **child,
                    "investment_in_529_plan_indv": 1_000.0,
                    "count_529_contribution_beneficiaries": 1,
                }
            ],
        },
    ]
    check(units)
    unit_results, _, _ = calculate(units)
    np.testing.assert_allclose(
        unit_results["oh_529_plan_deduction"], [4_100, 4_000, 4_000, 0]
    )
