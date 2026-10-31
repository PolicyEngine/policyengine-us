"""Invariants for dependents in Georgia's HB463 tip and overtime exclusions.

O.C.G.A. § 48-7-27(a) makes Georgia taxable net income "the taxpayer's
federal adjusted gross income ... less" its listed subtractions. HB463
(2026) adds two for tax years 2026 through 2028: (16)(A) "qualified overtime
compensation, as such term is defined in Section 225 of the Internal Revenue
Code, up to $1,750.00 received by a full-time employee paid by an hourly
wage", and (17)(A) "any amount up to $1,750.00 received in cash tips". A
dependent's tips and overtime are the dependent's own income (26 U.S.C.
73(a) for a child's services). They are not in the filer's federal AGI, so
the filer cannot subtract them. test_ga_overtime_exclusion_eligibility_
invariants.py covers the full-time and hourly tests.

Hypothesis draws batches of Georgia tax units (single, head of household
with dependents, joint with and without dependents), and a seeded population
of 150 units adds breadth. Heads, spouses and dependents each get wages,
tips in or outside a Treasury tipped occupation, and overtime premiums and
Railway Labor Act overtime, some above the cap. Everyone works full-time and
earns an hourly wage, so a dependent's overtime would count but for the rule
under test. Each batch runs as one vectorized simulation, twice: with the
dependents' tips, occupation codes and overtime as drawn and with them set
to zero. For every tax unit:

1. The dependents' tips and overtime never change either exclusion, Georgia
   subtractions, Georgia AGI, Georgia taxable income or Georgia income tax.
2. Differential: each exclusion equals an independent numpy sum, over the
   head and spouse only, of their own amount (tips only from a tipped
   occupation) capped at $1,750 each, restated from the statute rather than
   read from the parameter files. For units without dependents this is the
   previous all-member sum, so they see no change.
3. Each exclusion lies between 0 and $1,750 times the number of filers (one,
   or two on a joint return).

The seeded population also checks that it contains units whose dependents'
amounts would have changed the old all-member sum, so 1 and 2 are not
vacuous.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
# O.C.G.A. § 48-7-27(a)(16)(A) and (17)(A): "up to $1,750.00".
CAP = 1_750
# A Treasury Tipped Occupation Code (102, bartenders) and none.
TIPPED_CODE = 102
FULL_TIME_HOURLY = {"is_paid_hourly": True, "weekly_hours_worked_before_lsr": 40}

DEPENDENT_INPUTS = [
    "tip_income",
    "treasury_tipped_occupation_code",
    "fsla_overtime_premium",
    "ga_rla_hourly_component_overtime",
]
OUTPUTS = [
    "ga_cash_tip_exclusion",
    "ga_qualified_overtime_exclusion",
    "ga_subtractions",
    "ga_agi",
    "ga_taxable_income",
    "ga_income_tax",
]

tips = st.one_of(st.just(0.0), st.integers(1, 6_000).map(float))
overtime = st.one_of(st.just(0.0), st.integers(1, 4_000).map(float))


@st.composite
def person_amounts(draw):
    tip_income = draw(tips)
    overtime_premium = draw(overtime)
    rla_overtime = draw(overtime)
    # Tips and both overtime amounts are parts of employment income.
    base_wages = draw(st.integers(0, 60_000))
    return {
        "employment_income": (
            float(base_wages) + tip_income + overtime_premium + rla_overtime
        ),
        "tip_income": tip_income,
        "treasury_tipped_occupation_code": draw(st.sampled_from([0, TIPPED_CODE])),
        "fsla_overtime_premium": overtime_premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
        **FULL_TIME_HOURLY,
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": {"age": draw(st.integers(25, 70)), **draw(person_amounts())},
        "spouse": (
            {"age": draw(st.integers(25, 70)), **draw(person_amounts())}
            if kind.startswith("joint")
            else None
        ),
        "dependents": [
            {"age": draw(st.integers(14, 23)), **draw(person_amounts())}
            for _ in range(n_dependents)
        ],
    }


SEED = 20261023


def _seeded_amounts(rng):
    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    tip_income = some(1, 6_000, 0.6)
    overtime_premium = some(1, 4_000, 0.6)
    rla_overtime = some(1, 4_000, 0.2)
    return {
        "employment_income": (
            some(1, 60_000, 0.8) + tip_income + overtime_premium + rla_overtime
        ),
        "tip_income": tip_income,
        "treasury_tipped_occupation_code": TIPPED_CODE if rng.random() < 0.7 else 0,
        "fsla_overtime_premium": overtime_premium,
        "ga_rla_hourly_component_overtime": rla_overtime,
        **FULL_TIME_HOURLY,
    }


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": {"age": int(rng.integers(25, 71)), **_seeded_amounts(rng)},
                "spouse": (
                    {"age": int(rng.integers(25, 71)), **_seeded_amounts(rng)}
                    if kind.startswith("joint")
                    else None
                ),
                "dependents": [
                    {"age": int(rng.integers(14, 24)), **_seeded_amounts(rng)}
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "is_tax_unit_head": True,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": False,
            **u["head"],
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **u["spouse"],
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            amounts = dict(d)
            if zero_dependents:
                # Wages stay as drawn, so only the tip and overtime amounts
                # (and the occupation code) change.
                amounts.update({name: 0 for name in DEPENDENT_INPUTS})
            people[child] = {
                "is_full_time_student": d["age"] >= 19,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
                **amounts,
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "GA"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, zero_dependents):
    sim = Simulation(situation=_situation(units, year, zero_dependents=zero_dependents))
    out = {name: np.asarray(sim.calculate(name, year), dtype=float) for name in OUTPUTS}
    out["is_tax_unit_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    for name in DEPENDENT_INPUTS:
        out[name] = np.asarray(sim.calculate(name, year), dtype=float)
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"], weights=values, minlength=len(run["ga_cash_tip_exclusion"])
    )


def _amounts(run):
    """Each person's own tips (tipped occupation only) and overtime, capped."""
    tipped = run["treasury_tipped_occupation_code"] > 0
    overtime_total = (
        run["fsla_overtime_premium"] + run["ga_rla_hourly_component_overtime"]
    )
    return (
        np.minimum(run["tip_income"] * tipped, CAP),
        np.minimum(overtime_total, CAP),
    )


def _check(units, year, *, require_dependent_amounts=False):
    run = _run(units, year, zero_dependents=False)
    zeroed = _run(units, year, zero_dependents=True)
    filer = ~run["is_tax_unit_dependent"]

    # 1. Dependents' tips and overtime never reach the filer's Georgia return.
    for name in OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )

    # 2. Differential against numpy sums over the head and spouse.
    capped_tips, capped_overtime = _amounts(run)
    for name, capped in (
        ("ga_cash_tip_exclusion", capped_tips),
        ("ga_qualified_overtime_exclusion", capped_overtime),
    ):
        np.testing.assert_allclose(
            run[name], _unit_sum(run, filer * capped), atol=TOLERANCE, err_msg=name
        )
        has_dependent = _unit_sum(run, (~filer).astype(float)) > 0
        np.testing.assert_allclose(
            run[name][~has_dependent],
            _unit_sum(run, capped)[~has_dependent],
            atol=TOLERANCE,
            err_msg=name,
        )
        if require_dependent_amounts:
            # The old all-member sum differs from the filers' sum somewhere.
            leaked = _unit_sum(run, capped) - _unit_sum(run, filer * capped)
            assert (leaked > 0).sum() >= 10, name

    # 3. Bounds: 0 to $1,750 per filer.
    filers = _unit_sum(run, filer.astype(float))
    for name in ("ga_cash_tip_exclusion", "ga_qualified_overtime_exclusion"):
        assert (run[name] >= -TOLERANCE).all(), name
        assert (run[name] <= CAP * filers + TOLERANCE).all(), name


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
def test_dependents_tips_and_overtime_stay_off_the_filers_georgia_return(units):
    _check(units, 2026)


@pytest.mark.parametrize("year", [2026, 2028])
def test_seeded_population(year):
    _check(_seeded_units(), year, require_dependent_amounts=True)
