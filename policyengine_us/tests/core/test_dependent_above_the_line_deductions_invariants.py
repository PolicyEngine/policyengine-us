"""Invariants for dependents' above-the-line deductions in the filer's AGI.

A tax unit dependent's deductions belong on the dependent's own return: their
Schedule SE and Schedule 1 deductions (the deductible part of self-employment
tax, self-employed health insurance and retirement plans, the IRA deduction,
the penalty on early withdrawal of savings, educator expenses, alimony paid)
are figured with the dependent's own income. `irs_gross_income` already
leaves dependents' income off the filer's return, so every sum of
above-the-line deductions over a tax unit must leave dependents out too.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents, in Texas, Missouri and
Massachusetts), and a seeded population of 200 such units adds breadth. Each
batch runs as one vectorized simulation, twice: with
the dependents' deduction inputs as drawn and with them set to zero. For
every tax unit:

1. The dependents' deduction inputs never change the filer's AGI,
   above-the-line deductions, any tax-unit deduction aggregate, the Social
   Security and unemployment compensation MAGIs, taxable Social Security,
   Massachusetts gross income and Part B AGI, or the head's and spouse's
   per-person AGI,
   student loan interest MAGI and deduction, Medicaid AGI and Missouri AGI.
2. Accounting identities: the per-person AGIs of the members sum to the tax
   unit's AGI, and so do the head's and spouse's Medicaid AGIs.
3. Differential: `above_the_line_deductions` and each aggregate equal an
   independent numpy sum over the head and spouse. For units without
   dependents this is also the previous all-member sum, so they see no change.
4. Each person's own deduction amounts are still computed for dependents
   (half of each person's self-employment tax, for example), so a
   dependent's own return can use them, and a dependent's Medicaid AGI is
   their own gross income less their own person-level deductions.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Person-level inputs behind the deductions a dependent could claim on their
# own return.
DEPENDENT_DEDUCTION_INPUTS = [
    "self_employment_income",
    "self_employed_health_insurance_premiums",
    "self_employed_pension_contributions",
    "traditional_ira_contributions",
    "early_withdrawal_penalty",
    "educator_expense",
    "alimony_expense",
    "qualified_adoption_assistance_expense",
    "us_bonds_for_higher_ed",
    "student_loan_interest",
]
# Person-level deduction amounts that make up above_the_line_deductions,
# other than loss_ald and alimony_expense_ald.
PERSON_DEDUCTIONS = [
    "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald_person",
    "student_loan_interest_ald",
    "early_withdrawal_penalty",
    "educator_expense",
    "traditional_ira_contributions",
    "qualified_adoption_assistance_expense",
    "us_bonds_for_higher_ed",
]
AGGREGATES = {
    "self_employment_tax_ald": "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald": "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald": "self_employed_pension_contribution_ald_person",
}
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "above_the_line_deductions",
    *AGGREGATES,
    "alimony_expense_ald",
    "loss_ald",
    "taxable_ss_magi",
    "taxable_uc_agi",
    "tax_unit_taxable_social_security",
    "ma_gross_income",
    "ma_part_b_agi",
]
# Per-person outputs whose head and spouse values must not depend on the
# dependents' deductions.
FILER_PERSON_OUTPUTS = [
    "adjusted_gross_income_person",
    "student_loan_interest_ald_magi",
    "student_loan_interest_ald",
    "medicaid_adjusted_gross_income_person",
    "mo_adjusted_gross_income",
]
PERSON_OUTPUTS = [
    *FILER_PERSON_OUTPUTS,
    *PERSON_DEDUCTIONS,
    "self_employment_tax",
    "alimony_expense",
    "divorce_year",
    "medicaid_irs_gross_income",
    "irs_gross_income",
]

amount = st.integers(0, 40_000).map(float)
small = st.one_of(st.just(0.0), st.integers(1, 7_000).map(float))


@st.composite
def person_amounts(draw, *, dependent):
    has = st.booleans()
    return {
        "employment_income": draw(st.one_of(st.just(0.0), amount)),
        # Losses are loss_ald's business; draw mostly gains with some losses.
        "self_employment_income": (
            draw(st.integers(-10_000, 60_000).map(float)) if draw(has) else 0.0
        ),
        "self_employed_health_insurance_premiums": draw(small),
        "self_employed_pension_contributions": draw(small),
        "traditional_ira_contributions": draw(small),
        "early_withdrawal_penalty": draw(st.integers(0, 500).map(float)),
        "educator_expense": draw(st.integers(0, 300).map(float)),
        "alimony_expense": draw(small),
        "divorce_year": draw(st.sampled_from([2010, 2018, 2020])),
        "qualified_adoption_assistance_expense": draw(small),
        "us_bonds_for_higher_ed": draw(small),
        "student_loan_interest": draw(st.integers(0, 3_000).map(float)),
        "taxable_interest_income": draw(st.integers(0, 2_000).map(float)),
        "social_security_retirement": (
            0.0 if dependent else draw(st.one_of(st.just(0.0), amount))
        ),
        "taxable_private_pension_income": (
            0.0 if dependent else draw(st.one_of(st.just(0.0), amount))
        ),
        "unemployment_compensation": draw(
            st.one_of(st.just(0.0), st.integers(1, 15_000).map(float))
        ),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "state": draw(st.sampled_from(["TX", "MO", "MA"])),
        "head": draw(person_amounts(dependent=False)),
        "spouse": (
            draw(person_amounts(dependent=False)) if kind.startswith("joint") else None
        ),
        "dependents": [
            {
                "age": draw(st.integers(5, 23)),
                **draw(person_amounts(dependent=True)),
            }
            for _ in range(n_dependents)
        ],
    }


SEED = 20261005


def _seeded_amounts(rng, *, dependent):
    def some(high, p=0.5):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    return {
        "employment_income": some(40_000, 0.6),
        "self_employment_income": (
            float(round(rng.uniform(-10_000, 60_000))) if rng.random() < 0.6 else 0.0
        ),
        "self_employed_health_insurance_premiums": some(7_000),
        "self_employed_pension_contributions": some(7_000),
        "traditional_ira_contributions": some(7_000),
        "early_withdrawal_penalty": some(500),
        "educator_expense": some(300),
        "alimony_expense": some(7_000, 0.3),
        "divorce_year": int(rng.choice([2010, 2018, 2020])),
        "qualified_adoption_assistance_expense": some(7_000, 0.2),
        "us_bonds_for_higher_ed": some(7_000, 0.2),
        "student_loan_interest": some(3_000),
        "taxable_interest_income": some(2_000),
        "social_security_retirement": 0.0 if dependent else some(40_000, 0.3),
        "taxable_private_pension_income": 0.0 if dependent else some(40_000, 0.3),
        "unemployment_compensation": some(15_000, 0.2),
    }


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "state": str(rng.choice(["TX", "MO", "MA"])),
                "head": _seeded_amounts(rng, dependent=False),
                "spouse": (
                    _seeded_amounts(rng, dependent=False)
                    if kind.startswith("joint")
                    else None
                ),
                "dependents": [
                    {
                        "age": int(rng.integers(5, 24)),
                        **_seeded_amounts(rng, dependent=True),
                    }
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
            "age": 50,
            "is_tax_unit_head": True,
            "is_tax_unit_spouse": False,
            "is_tax_unit_dependent": False,
            **u["head"],
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": 48,
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
            amounts = {k: v for k, v in d.items() if k != "age"}
            if zero_dependents:
                amounts.update({name: 0.0 for name in DEPENDENT_DEDUCTION_INPUTS})
            people[child] = {
                "age": d["age"],
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
            "state_code": {year: u["state"]},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, zero_dependents):
    sim = Simulation(situation=_situation(units, year, zero_dependents=zero_dependents))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in TAX_UNIT_OUTPUTS + PERSON_OUTPUTS
    }
    out["filing_status"] = np.asarray(sim.calculate("filing_status", year))
    out["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"], weights=values, minlength=len(run["adjusted_gross_income"])
    )


def _check(units, year):
    run = _run(units, year, zero_dependents=False)
    zeroed = _run(units, year, zero_dependents=True)
    filer = ~run["is_dependent"]
    has_dependent = _unit_sum(run, run["is_dependent"].astype(float)) > 0

    # 1. Dependents' deduction inputs never reach the filer's return.
    assert (run["filing_status"] == zeroed["filing_status"]).all()
    for name in TAX_UNIT_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )
    for name in FILER_PERSON_OUTPUTS:
        np.testing.assert_allclose(
            run[name][filer], zeroed[name][filer], atol=TOLERANCE, err_msg=name
        )

    # 2. Accounting identities.
    np.testing.assert_allclose(
        _unit_sum(run, run["adjusted_gross_income_person"]),
        run["adjusted_gross_income"],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _unit_sum(run, filer * run["medicaid_adjusted_gross_income_person"]),
        run["adjusted_gross_income"],
        atol=TOLERANCE,
    )

    # 3. Differential against numpy sums over the head and spouse. Alimony
    # is deductible for divorces before 2019 (26 USC 215, repealed by Pub. L.
    # 115-97 sec. 11051 for later instruments).
    alimony = run["alimony_expense"] * (run["divorce_year"] < 2019)
    np.testing.assert_allclose(
        run["alimony_expense_ald"], _unit_sum(run, filer * alimony), atol=TOLERANCE
    )
    for aggregate, person_amount in AGGREGATES.items():
        np.testing.assert_allclose(
            run[aggregate],
            _unit_sum(run, filer * run[person_amount]),
            atol=TOLERANCE,
            err_msg=aggregate,
        )
    person_total = sum(run[name] for name in PERSON_DEDUCTIONS)
    reference = run["loss_ald"] + _unit_sum(run, filer * (person_total + alimony))
    np.testing.assert_allclose(
        run["above_the_line_deductions"], reference, atol=TOLERANCE
    )
    # Units without dependents: the previous all-member sum, unchanged.
    all_members = run["loss_ald"] + _unit_sum(run, person_total + alimony)
    np.testing.assert_allclose(
        run["above_the_line_deductions"][~has_dependent],
        all_members[~has_dependent],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        run["adjusted_gross_income"],
        _unit_sum(run, run["irs_gross_income"]) - reference,
        atol=TOLERANCE,
    )

    # 4. Each person's own amounts survive for their own return.
    np.testing.assert_allclose(
        run["self_employment_tax_ald_person"],
        0.5 * run["self_employment_tax"],
        atol=TOLERANCE,
    )
    dependent = run["is_dependent"]
    own_person_deductions = person_total - run["student_loan_interest_ald"]
    np.testing.assert_allclose(
        run["medicaid_adjusted_gross_income_person"][dependent],
        (run["medicaid_irs_gross_income"] - own_person_deductions)[dependent],
        atol=TOLERANCE,
    )
    assert (run["student_loan_interest_ald"][dependent] == 0).all()
    assert (run["adjusted_gross_income_person"][dependent] == 0).all()


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
def test_dependent_deductions_stay_off_the_filers_return_2025(units):
    _check(units, 2025)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_dependent_deductions_stay_off_the_filers_return_2020(units):
    # 2020 adds the unemployment compensation exclusion, which reads
    # taxable_uc_agi, and the tuition and fees deduction.
    _check(units, 2020)


@pytest.mark.parametrize("year", [2020, 2025])
def test_seeded_population(year):
    _check(_seeded_units(), year)
