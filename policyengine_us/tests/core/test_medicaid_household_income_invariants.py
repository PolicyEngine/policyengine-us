"""Invariants for Medicaid MAGI household income when members have losses.

Household income is the sum of the MAGI-based income of every member of the
household (42 CFR 435.603(d)(1)), figured with the 36B methodology
(435.603(e)). On a joint return the couple has one AGI, so one spouse's loss
offsets the other's income, and Form 8962 line 3 combines the couple's and
their dependents' modified AGIs "even if one or both of them are negative"
before entering a negative total as zero. So no member's MAGI-based income is
floored; only the household's total is.

Hypothesis draws batches of households: joint filers with up to two
dependent children, a married couple who do not file, cohabiting spouses who
file separately, and single filers. Spouses draw wages, self-employment and
rental income that can be losses, capital gains or losses, interest, Social
Security, and their own IRA, early withdrawal penalty, student loan interest
and alimony deductions. Children draw wages, interest, tax-exempt interest and
IRA contributions, so some are required to file. A seeded population of 200
households adds breadth. Each batch runs as one vectorized simulation, and
again with metamorphic changes. For every household:

1. Joint filers: each member's household income is
   max(0, J + D), where J is the couple's MAGI, figured independently from
   the tax unit's adjusted_gross_income plus the MAGI additions, and D is the
   sum of the MAGI of the children required to file. When J >= 0 and every
   counted child's MAGI is >= 0 this is max(0, J) + D.
2. Accounting: the head's and spouse's medicaid_magi_person add up to J, and
   a dependent's Medicaid AGI is their own gross income less their own
   above-the-line deductions.
3. Non-filing couples and cohabiting spouses filing separately: each
   spouse's household income is max(0, the two spouses' MAGI added).
   Single filers: max(0, their MAGI).
4. Household income is never negative, and is zero exactly when the
   unfloored sum is not positive.
5. Metamorphic: removing the spouse's own IRA deduction, early withdrawal
   penalty and alimony leaves the head's own deductions unchanged; swapping
   the head's and spouse's incomes and deductions leaves every member's
   household income unchanged; and lowering the spouse's self-employment
   income never raises household income.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01  # dollars

# Each spouse's own deductions that no other member's inputs limit. Student
# loan interest and capital losses are limited for the return as a whole, so
# one spouse's amount can change the other's share.
SPOUSE_ONLY_DEDUCTION_INPUTS = [
    "traditional_ira_contributions",
    "early_withdrawal_penalty",
    "alimony_expense",
]
OUTPUTS = [
    "medicaid_household_income",
    "medicaid_magi_person",
    "medicaid_adjusted_gross_income_person",
    "medicaid_irs_gross_income",
    "medicaid_person_is_required_to_file",
    "medicaid_uses_non_filer_rules",
    "above_the_line_deductions_person",
    "student_loan_interest_ald",
    "tax_exempt_interest_income",
]
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "tax_exempt_social_security",
    "foreign_earned_income_exclusion",
]

amount = st.integers(1, 60_000).map(float)
maybe = lambda strategy: st.one_of(st.just(0.0), strategy)  # noqa: E731


@st.composite
def spouse_amounts(draw):
    return {
        "employment_income": draw(maybe(amount)),
        "self_employment_income": draw(maybe(st.integers(-40_000, 60_000).map(float))),
        "rental_income": draw(maybe(st.integers(-15_000, 20_000).map(float))),
        "long_term_capital_gains": draw(maybe(st.integers(-10_000, 10_000).map(float))),
        "taxable_interest_income": draw(maybe(st.integers(1, 3_000).map(float))),
        "tax_exempt_interest_income": draw(maybe(st.integers(1, 2_000).map(float))),
        "social_security_retirement": draw(maybe(st.integers(1, 30_000).map(float))),
        "traditional_ira_contributions": draw(maybe(st.integers(1, 7_000).map(float))),
        "early_withdrawal_penalty": draw(maybe(st.integers(1, 500).map(float))),
        "student_loan_interest": draw(maybe(st.integers(1, 3_000).map(float))),
        "alimony_expense": draw(maybe(st.integers(1, 12_000).map(float))),
        "divorce_year": draw(st.sampled_from([2010, 2020])),
    }


@st.composite
def child_amounts(draw):
    return {
        "age": draw(st.integers(5, 17)),
        "employment_income": draw(maybe(st.integers(1, 30_000).map(float))),
        "taxable_interest_income": draw(maybe(st.integers(1, 3_000).map(float))),
        "tax_exempt_interest_income": draw(maybe(st.integers(1, 1_000).map(float))),
        "traditional_ira_contributions": draw(maybe(st.integers(1, 3_000).map(float))),
    }


@st.composite
def households(draw):
    kind = draw(st.sampled_from(["joint", "joint", "non_filer", "separate", "single"]))
    n_children = draw(st.integers(0, 2)) if kind == "joint" else 0
    return {
        "kind": kind,
        "head": draw(spouse_amounts()),
        "spouse": None if kind == "single" else draw(spouse_amounts()),
        "children": [draw(child_amounts()) for _ in range(n_children)],
    }


SEED = 20261006


def _seeded_households(n=200):
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def spouse():
        return {
            "employment_income": some(1, 60_000, 0.6),
            "self_employment_income": some(-40_000, 60_000, 0.4),
            "rental_income": some(-15_000, 20_000, 0.2),
            "long_term_capital_gains": some(-10_000, 10_000, 0.2),
            "taxable_interest_income": some(1, 3_000),
            "tax_exempt_interest_income": some(1, 2_000, 0.2),
            "social_security_retirement": some(1, 30_000, 0.2),
            "traditional_ira_contributions": some(1, 7_000, 0.3),
            "early_withdrawal_penalty": some(1, 500, 0.2),
            "student_loan_interest": some(1, 3_000, 0.3),
            "alimony_expense": some(1, 12_000, 0.2),
            "divorce_year": int(rng.choice([2010, 2020])),
        }

    units = []
    for _ in range(n):
        kind = str(rng.choice(["joint", "joint", "non_filer", "separate", "single"]))
        n_children = int(rng.integers(0, 3)) if kind == "joint" else 0
        units.append(
            {
                "kind": kind,
                "head": spouse(),
                "spouse": None if kind == "single" else spouse(),
                "children": [
                    {
                        "age": int(rng.integers(5, 18)),
                        "employment_income": some(1, 30_000),
                        "taxable_interest_income": some(1, 3_000),
                        "tax_exempt_interest_income": some(1, 1_000, 0.3),
                        "traditional_ira_contributions": some(1, 3_000, 0.3),
                    }
                    for _ in range(n_children)
                ],
            }
        )
    return units


def _situation(units):
    people = {}
    groups = {
        "tax_units": {},
        "households": {},
        "marital_units": {},
        "families": {},
        "spm_units": {},
    }
    kinds, roles = [], []
    for i, u in enumerate(units):
        head, spouse = f"head_{i}", f"spouse_{i}"
        people[head] = {"age": 45, **u["head"]}
        members, roles_i = [head], ["head"]
        if u["spouse"] is not None:
            people[spouse] = {"age": 45, **u["spouse"]}
            members.append(spouse)
            roles_i.append("spouse")
            groups["marital_units"][f"couple_{i}"] = {"members": [head, spouse]}
        else:
            groups["marital_units"][f"couple_{i}"] = {"members": [head]}
        if u["kind"] == "separate":
            people[head]["is_tax_unit_head"] = True
            people[spouse]["is_tax_unit_head"] = True
            for name, member in (("a", head), ("b", spouse)):
                groups["tax_units"][f"tax_unit_{i}{name}"] = {
                    "members": [member],
                    "cohabitating_spouses": {YEAR: True},
                    "tax_unit_is_filer": {YEAR: True},
                }
        else:
            people[head]["is_tax_unit_head"] = True
            if u["spouse"] is not None:
                people[spouse]["is_tax_unit_spouse"] = True
        for j, child in enumerate(u["children"]):
            name = f"child_{i}_{j}"
            people[name] = {"is_tax_unit_dependent": True, **child}
            members.append(name)
            roles_i.append("child")
            groups["marital_units"][f"child_{i}_{j}"] = {"members": [name]}
        if u["kind"] != "separate":
            groups["tax_units"][f"tax_unit_{i}"] = {
                "members": members,
                "tax_unit_is_filer": {YEAR: u["kind"] != "non_filer"},
            }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
        # Each household is its own family, so the non-filer rules' parents
        # and children come from the household only.
        groups["families"][f"family_{i}"] = {"members": members}
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        kinds += [u["kind"]] * len(members)
        roles += roles_i
    people = {
        name: {k: {YEAR: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}, np.array(kinds), np.array(roles)


def _run(units):
    situation, kinds, roles = _situation(units)
    sim = Simulation(situation=situation)
    out = {name: np.asarray(sim.calculate(name, YEAR), dtype=float) for name in OUTPUTS}
    for name in TAX_UNIT_OUTPUTS:
        out[name] = np.asarray(sim.calculate(name, YEAR, map_to="person"), dtype=float)
    out["kind"], out["role"] = kinds, roles
    # People are listed household by household, so the household index
    # groups each household's members.
    out["household"] = sim.populations["household"].members_entity_id
    return out


def _household_sum(run, values):
    return np.bincount(run["household"], weights=values)[run["household"]]


def _swap_spouses(units):
    swapped = []
    for u in units:
        if u["spouse"] is None:
            swapped.append(u)
        else:
            swapped.append({**u, "head": u["spouse"], "spouse": u["head"]})
    return swapped


def _without_spouse_deductions(units):
    changed = []
    for u in units:
        if u["spouse"] is None:
            changed.append(u)
            continue
        spouse = {**u["spouse"], **{k: 0.0 for k in SPOUSE_ONLY_DEDUCTION_INPUTS}}
        changed.append({**u, "spouse": spouse})
    return changed


def _lower_spouse_self_employment(units, by=7_500.0):
    changed = []
    for u in units:
        if u["spouse"] is None:
            changed.append(u)
            continue
        spouse = {
            **u["spouse"],
            "self_employment_income": u["spouse"]["self_employment_income"] - by,
        }
        changed.append({**u, "spouse": spouse})
    return changed


def _check(units):
    run = _run(units)
    income = run["medicaid_household_income"]
    magi = run["medicaid_magi_person"]
    kind, role = run["kind"], run["role"]
    adult = role != "child"
    child = role == "child"
    counted_child = child & (run["medicaid_person_is_required_to_file"] > 0)

    # 4. Never negative.
    assert (income >= 0).all()

    # 1 and 2. Joint filers. The couple's MAGI, from the tax unit's AGI and
    # the MAGI additions (36B(d)(2)(B)): the head's and spouse's tax-exempt
    # interest, the foreign earned income exclusion and nontaxable Social
    # Security, which the children here do not have.
    joint = kind == "joint"
    couple_magi = (
        run["adjusted_gross_income"]
        + _household_sum(run, adult * run["tax_exempt_interest_income"])
        + run["foreign_earned_income_exclusion"]
        + run["tax_exempt_social_security"]
    )
    np.testing.assert_allclose(
        _household_sum(run, adult * magi)[joint],
        couple_magi[joint],
        atol=TOLERANCE,
        err_msg="spouses' MAGI do not add up to the couple's MAGI",
    )
    children_magi = _household_sum(run, counted_child * magi)
    assert not run["medicaid_uses_non_filer_rules"][joint].any()
    np.testing.assert_allclose(
        income[joint],
        np.maximum(0, couple_magi + children_magi)[joint],
        atol=TOLERANCE,
        err_msg="joint household income is not max(0, J + D)",
    )
    nonnegative = (couple_magi >= 0) & (
        _household_sum(run, counted_child * (magi < 0)) == 0
    )
    np.testing.assert_allclose(
        income[joint & nonnegative],
        (np.maximum(0, couple_magi) + children_magi)[joint & nonnegative],
        atol=TOLERANCE,
    )
    # A dependent's Medicaid AGI is their own gross income less their own
    # deductions.
    np.testing.assert_allclose(
        run["medicaid_adjusted_gross_income_person"][child],
        (run["medicaid_irs_gross_income"] - run["above_the_line_deductions_person"])[
            child
        ],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        magi[child],
        (
            run["medicaid_adjusted_gross_income_person"]
            + run["tax_exempt_interest_income"]
        )[child],
        atol=TOLERANCE,
    )

    # 3. Couples outside a joint return, and single filers.
    pair = (kind == "non_filer") | (kind == "separate")
    np.testing.assert_allclose(
        income[pair],
        np.maximum(0, _household_sum(run, magi))[pair],
        atol=TOLERANCE,
        err_msg="spouses outside a joint return are not netted",
    )
    single = kind == "single"
    np.testing.assert_allclose(
        income[single], np.maximum(0, magi)[single], atol=TOLERANCE
    )

    # 4. Zero exactly when the unfloored sum is not positive.
    unfloored = np.where(
        joint,
        couple_magi + children_magi,
        np.where(pair, _household_sum(run, magi), magi),
    )
    np.testing.assert_allclose(income, np.maximum(0, unfloored), atol=TOLERANCE)
    assert (income[unfloored <= 0] == 0).all()

    # 5. Metamorphic relations. The spouse's own deductions never change the
    # head's deductions, other than the student loan interest deduction,
    # whose phase-out reads the couple's joint MAGI.
    head = role == "head"
    without = _run(_without_spouse_deductions(units))
    head_deductions = (
        run["above_the_line_deductions_person"] - run["student_loan_interest_ald"]
    )
    np.testing.assert_allclose(
        (
            without["above_the_line_deductions_person"]
            - without["student_loan_interest_ald"]
        )[head],
        head_deductions[head],
        atol=TOLERANCE,
        err_msg="the spouse's own deductions changed the head's deductions",
    )
    swapped = _run(_swap_spouses(units))
    np.testing.assert_allclose(
        swapped["medicaid_household_income"],
        income,
        atol=TOLERANCE,
        err_msg="swapping the spouses changed household income",
    )
    lowered = _run(_lower_spouse_self_employment(units))
    assert (lowered["medicaid_household_income"] <= income + TOLERANCE).all()


SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(households(), min_size=10, max_size=40))
def test_medicaid_household_income_nets_members_before_the_floor(units):
    _check(units)


def test_seeded_population():
    _check(_seeded_households())


@pytest.mark.parametrize(
    "head, spouse, expected",
    [
        # The brief's example: 30,000 of wages and a 20,000 Schedule C loss.
        (
            {"employment_income": 30_000.0},
            {"self_employment_income": -20_000.0},
            10_000,
        ),
        # One spouse's 6,000 IRA deduction, the other spouse with no income.
        (
            {"employment_income": 30_000.0, "traditional_ira_contributions": 6_000.0},
            {},
            24_000,
        ),
    ],
)
def test_joint_examples(head, spouse, expected):
    units = [{"kind": "joint", "head": head, "spouse": spouse, "children": []}]
    run = _run(units)
    np.testing.assert_allclose(
        run["medicaid_household_income"], [expected, expected], atol=TOLERANCE
    )


@settings(**SETTINGS)
@given(st.lists(st.integers(-60_000, 60_000), min_size=6, max_size=6))
def test_linked_non_filer_income_matches_signed_legal_membership(magi):
    """Linked members net signed income; excluded relatives cannot affect it.

    The two unmarried parents share two children. The grandmother and an
    unrelated adult live in the same family and household. Under
    42 CFR 435.603(f)(3), each parent's household includes their children,
    and each child's includes both parents and their sibling. Neither child
    includes the grandmother or unrelated adult. All members' counted MAGI
    is supplied directly so this property isolates membership and netting.
    """
    names = ["grandmother", "mother", "father", "child", "sibling", "unrelated"]
    ages = [65, 35, 35, 10, 12, 30]
    people = {
        name: {
            "person_id": i + 1,
            "age": {YEAR: ages[i]},
            "medicaid_magi_person": {YEAR: magi[i]},
            # Count the children's MAGI under 435.603(d)(2)(i), including
            # negative amounts. Filing flags are inputs to this income test.
            "medicaid_person_is_required_to_file": {YEAR: True},
        }
        for i, name in enumerate(names)
    }
    people["mother"]["parent_1_id"] = 1
    for child in ("child", "sibling"):
        people[child].update(parent_1_id=2, parent_2_id=3)
    situation = {
        "people": people,
        "tax_units": {
            name: {"members": [name], "tax_unit_is_filer": {YEAR: False}}
            for name in names
        },
        "marital_units": {name: {"members": [name]} for name in names},
        "families": {"family": {"members": names}},
        "households": {"home": {"members": names, "state_code": {YEAR: "OH"}}},
    }
    # Independent reference membership, rather than reusing a model helper.
    members = np.array(
        [
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ]
    )
    simulation = Simulation(situation=situation)
    assert simulation.calculate("medicaid_uses_non_filer_rules", YEAR).all()
    np.testing.assert_array_equal(
        simulation.calculate("medicaid_household_size", YEAR), members.sum(axis=1)
    )
    np.testing.assert_allclose(
        simulation.calculate("medicaid_household_income", YEAR),
        np.maximum(0, members @ np.asarray(magi)),
        atol=TOLERANCE,
    )
