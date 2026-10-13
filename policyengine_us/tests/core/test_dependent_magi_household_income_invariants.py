"""Invariants for dependents' income in ACA and Medicaid household income.

Household income counts another member's modified AGI only if that member is
required to file a return (26 CFR 1.36B-1(e)(1)(ii); 42 CFR 435.603(d)(2)).
So `medicaid_magi`, which `aca_magi` adds, is the head's and spouse's modified
AGI plus the whole modified AGI of each tax unit dependent who must file, and
each person's Social Security is their own (`tax_exempt_social_security_person`).

Hypothesis draws batches of tax units (single, head of household, joint with
and without dependents) whose members have wages, taxable and tax-exempt
interest, and Social Security, and a seeded population of 200 such units adds
breadth. Dependents are children and disabled adult children, with benefits up
to $60,000 so that some are taxable on the dependent's own return. Each batch
runs as one vectorized simulation twice: as drawn, and with every dependent's
tax-exempt interest and Social Security set to zero. For every tax unit:

1. Differential: `medicaid_magi` equals an independent numpy computation of
   Form 8962 lines 2a, 2b and 3: the return's AGI plus the filers' tax-exempt
   interest and untaxed benefits, plus, for each dependent required to file
   under IRS Pub. 501 Table 2, their wages, interest, tax-exempt interest and
   all their benefits, floored at zero. The dependents' taxable benefits (IRC
   86 on their own income) and filing requirements match the same computation.
2. Exclusion: where no dependent must file, removing the dependents'
   tax-exempt interest and benefits leaves `medicaid_magi` unchanged, and it
   never changes the head's or spouse's `medicaid_magi_person`.
3. Identities: each person's tax-exempt, filer-taxable and dependent-taxable
   benefits add up to their benefits; the head's and spouse's tax-exempt
   benefits add up to `filer_tax_exempt_social_security`; `aca_magi` equals
   `medicaid_magi`, which is never negative.
4. Without dependents, `medicaid_magi` equals the previous formula, AGI plus
   every member's tax-exempt interest plus `tax_exempt_social_security`.
5. Where everyone in the tax unit follows the tax-filer rules, each member's
   person-level Medicaid household income equals `medicaid_magi`.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# IRC 86(c)(1)(A), (c)(2)(A) and (a): statutory, not indexed.
SS_BASE = 25_000
SS_ADJUSTED_BASE = 34_000

OUTPUTS = [
    "adjusted_gross_income",
    "medicaid_magi",
    "aca_magi",
    "tax_unit_taxable_social_security",
    "tax_exempt_social_security",
    "filer_tax_exempt_social_security",
]
PERSON_OUTPUTS = [
    "medicaid_person_is_required_to_file",
    "dependent_taxable_social_security",
    "taxable_social_security",
    "tax_exempt_social_security_person",
    "social_security",
    "medicaid_magi_person",
    "medicaid_household_income",
    "medicaid_uses_non_filer_rules",
]
INPUTS = [
    "employment_income",
    "taxable_interest_income",
    "tax_exempt_interest_income",
]

small = st.one_of(st.just(0.0), st.integers(1, 4_000).map(float))
wages = st.one_of(st.just(0.0), st.integers(1, 30_000).map(float))
benefits = st.one_of(st.just(0.0), st.integers(1, 60_000).map(float))


@st.composite
def person_amounts(draw):
    return {
        "employment_income": draw(wages),
        "taxable_interest_income": draw(small),
        "tax_exempt_interest_income": draw(small),
        "social_security": draw(benefits),
    }


@st.composite
def dependents(draw):
    adult = draw(st.booleans())
    return {
        "age": draw(st.integers(19, 40)) if adult else draw(st.integers(1, 17)),
        "disabled": adult,
        **draw(person_amounts()),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(person_amounts()),
        "spouse": draw(person_amounts()) if kind.startswith("joint") else None,
        "dependents": [draw(dependents()) for _ in range(n_dependents)],
    }


SEED = 20261011


def _seeded_amounts(rng):
    def some(high, p=0.5):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    return {
        "employment_income": some(30_000),
        "taxable_interest_income": some(4_000),
        "tax_exempt_interest_income": some(4_000),
        "social_security": some(60_000),
    }


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        deps = []
        for _ in range(n_dependents):
            adult = bool(rng.random() < 0.3)
            deps.append(
                {
                    "age": int(rng.integers(19, 41) if adult else rng.integers(1, 18)),
                    "disabled": adult,
                    **_seeded_amounts(rng),
                }
            )
        units.append(
            {
                "head": _seeded_amounts(rng),
                "spouse": _seeded_amounts(rng) if kind.startswith("joint") else None,
                "dependents": deps,
            }
        )
    return units


def _inputs(amounts, benefit_variable):
    values = {name: amounts[name] for name in INPUTS}
    values[benefit_variable] = amounts["social_security"]
    return values


def _situation(units, year, *, zero_dependents_untaxed=False):
    people = {}
    groups = {
        "tax_units": {},
        "households": {},
        "marital_units": {},
        "families": {},
        "spm_units": {},
    }
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 45,
            "is_tax_unit_head": True,
            "is_tax_unit_dependent": False,
            **_inputs(u["head"], "social_security_retirement"),
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": 43,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **_inputs(u["spouse"], "social_security_retirement"),
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            values = _inputs(d, "social_security_survivors")
            if zero_dependents_untaxed:
                values["tax_exempt_interest_income"] = 0.0
                values["social_security_survivors"] = 0.0
            people[child] = {
                "age": d["age"],
                "is_disabled": d["disabled"],
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
                **values,
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
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
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in OUTPUTS + PERSON_OUTPUTS
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["parameters"] = sim.tax_benefit_system.parameters(f"{year}-01-01")
    return out


def _by_person(units, key):
    """Person-level input values in member order; key "role" gives a flag
    for dependents."""
    rows = []
    for u in units:
        rows.append((u["head"], False))
        if u["spouse"] is not None:
            rows.append((u["spouse"], False))
        rows += [(d, True) for d in u["dependents"]]
    if key == "role":
        return np.array([dependent for _, dependent in rows])
    return np.array([amounts[key] for amounts, _ in rows], dtype=float)


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=len(run["medicaid_magi"]))


def _dependent_taxable_benefits(modified_agi, benefits):
    # IRC 86(a) and (b) on a single dependent's own return.
    combined = modified_agi + benefits / 2
    tier_1 = np.minimum(benefits / 2, (combined - SS_BASE) / 2)
    tier_2 = np.minimum(
        0.85 * (combined - SS_ADJUSTED_BASE)
        + np.minimum(benefits / 2, (SS_ADJUSTED_BASE - SS_BASE) / 2),
        0.85 * benefits,
    )
    return np.where(
        combined < SS_BASE, 0, np.where(combined < SS_ADJUSTED_BASE, tier_1, tier_2)
    )


def _check(units, year):
    run = _run(units, year)
    zeroed = _run(units, year, zero_dependents_untaxed=True)
    dependent = _by_person(units, "role")
    filer = ~dependent
    wages_ = _by_person(units, "employment_income")
    interest = _by_person(units, "taxable_interest_income")
    exempt_interest = _by_person(units, "tax_exempt_interest_income")
    benefits_ = _by_person(units, "social_security")
    np.testing.assert_allclose(run["social_security"], benefits_, atol=TOLERANCE)

    # 1. Differential: Form 8962 lines 2a, 2b and 3 from the inputs.
    standard = run["parameters"].gov.irs.deductions.standard
    dependent_amount = standard.dependent.amount
    earned_addition = standard.dependent.additional_earned_income
    single_amount = standard.amount["SINGLE"]
    taxable = _dependent_taxable_benefits(
        wages_ + interest + exempt_interest, benefits_
    )
    gross = wages_ + interest + taxable
    required = (
        (interest + taxable > dependent_amount)
        | (wages_ > single_amount)
        | (
            gross
            > np.minimum(
                single_amount, np.maximum(dependent_amount, wages_ + earned_addition)
            )
        )
    )
    np.testing.assert_allclose(
        run["dependent_taxable_social_security"][dependent],
        taxable[dependent],
        atol=TOLERANCE,
    )
    np.testing.assert_array_equal(
        run["medicaid_person_is_required_to_file"][dependent].astype(bool),
        required[dependent],
    )
    filer_magi = (
        run["adjusted_gross_income"]
        + _unit_sum(run, filer * (exempt_interest + benefits_))
        - run["tax_unit_taxable_social_security"]
    )
    dependent_magi = wages_ + interest + exempt_interest + benefits_
    line_2b = _unit_sum(run, (dependent & required) * dependent_magi)
    expected = np.maximum(0, filer_magi + line_2b)
    np.testing.assert_allclose(run["medicaid_magi"], expected, atol=TOLERANCE)

    # 2. Exclusion: a dependent who need not file adds nothing, and the
    # filers' own Medicaid MAGI never holds a dependent's benefits.
    any_required = _unit_sum(run, (dependent & required).astype(float)) > 0
    np.testing.assert_allclose(
        run["medicaid_magi"][~any_required],
        zeroed["medicaid_magi"][~any_required],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        run["medicaid_magi_person"][filer],
        zeroed["medicaid_magi_person"][filer],
        atol=TOLERANCE,
    )

    # 3. Identities.
    np.testing.assert_allclose(
        run["tax_exempt_social_security_person"]
        + run["taxable_social_security"]
        + run["dependent_taxable_social_security"],
        run["social_security"],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _unit_sum(run, filer * run["tax_exempt_social_security_person"]),
        run["filer_tax_exempt_social_security"],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(run["aca_magi"], run["medicaid_magi"], atol=TOLERANCE)
    assert (run["medicaid_magi"] >= 0).all()

    # 4. Without dependents, the previous formula.
    has_dependent = _unit_sum(run, dependent.astype(float)) > 0
    previous = np.maximum(
        0,
        run["adjusted_gross_income"]
        + _unit_sum(run, exempt_interest)
        + run["tax_exempt_social_security"],
    )
    np.testing.assert_allclose(
        run["medicaid_magi"][~has_dependent],
        previous[~has_dependent],
        atol=TOLERANCE,
    )

    # 5. The person-level Medicaid household income agrees with the tax
    # unit's where every member follows the tax-filer rules.
    tax_route = _unit_sum(run, run["medicaid_uses_non_filer_rules"]) == 0
    person_tax_route = tax_route[run["unit"]]
    np.testing.assert_allclose(
        run["medicaid_household_income"][person_tax_route],
        run["medicaid_magi"][run["unit"]][person_tax_route],
        atol=TOLERANCE,
    )
    return has_dependent, any_required, tax_route


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
def test_dependent_magi_counts_only_when_required_to_file(units):
    _check(units, 2025)


@pytest.mark.parametrize("year", [2025, 2026])
def test_seeded_population(year):
    has_dependent, any_required, tax_route = _check(_seeded_units(), year)
    # The population exercises both branches of each property.
    assert has_dependent.sum() > 50
    assert any_required.sum() > 20
    assert (has_dependent & ~any_required).sum() > 20
    assert tax_route.sum() > 50
