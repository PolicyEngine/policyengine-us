"""Invariants for dependents' above-the-line deductions in the filer's AGI.

A tax unit dependent's deductions belong on the dependent's own return: their
Schedule SE and Schedule 1 deductions (the deductible part of self-employment
tax, self-employed health insurance and retirement plans, the IRA deduction,
the penalty on early withdrawal of savings, educator expenses, alimony paid)
are figured with the dependent's own income. `irs_gross_income` already
leaves dependents' income off the filer's return, so every sum of
above-the-line deductions over a tax unit must leave dependents out too.
Three amounts are the filer's whatever member they are recorded on, and are
summed over every member: employer adoption assistance and education savings
bond interest (`gov.irs.ald.filer_amounts_recorded_on_dependents`), and,
through 2020, a dependent's tuition in the tuition and fees deduction.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents, in Texas, Missouri,
Massachusetts and Minnesota), and a seeded population of 200 such units adds
breadth. Each
batch runs as one vectorized simulation, twice: with
the dependents' deduction inputs as drawn and with them set to zero. For
every tax unit:

1. The dependents' deduction inputs never change the filer's AGI,
   above-the-line deductions, any tax-unit deduction aggregate, the Social
   Security and unemployment compensation MAGIs, taxable Social Security,
   Massachusetts gross income and Part B AGI, Minnesota property tax refund
   household income, or the head's and spouse's per-person AGI, student loan
   interest MAGI and deduction, Medicaid AGI and Missouri AGI.
2. Accounting identities: the per-person AGIs of the members sum to the tax
   unit's AGI, and so do the head's and spouse's Medicaid AGIs.
3. Differential: `above_the_line_deductions` and each aggregate equal an
   independent numpy sum over the head and spouse (plus the three filer
   amounts over every member). For units without
   dependents this is also the previous all-member sum, so they see no change;
   for others it is between 0 and that sum.
4. Each person's own deduction amounts are still computed for dependents
   (half of each person's self-employment tax, for example), so a
   dependent's own return can use them, and a dependent's Medicaid AGI is
   their own gross income less their own deductions, alimony paid included.
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
    "student_loan_interest",
]
# Person-level deduction amounts in above_the_line_deductions that belong on
# each person's own return.
PERSON_DEDUCTIONS = [
    "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald_person",
    "alimony_expense_ald_person",
    "student_loan_interest_ald",
    "early_withdrawal_penalty",
    "educator_expense",
    "traditional_ira_contributions",
]
# Person-level amounts that are the filer's wherever they are recorded.
FILER_AMOUNTS = [
    "qualified_adoption_assistance_expense",
    "us_bonds_for_higher_ed",
]
AGGREGATES = {
    "self_employment_tax_ald": "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald": "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald": "self_employed_pension_contribution_ald_person",
    "alimony_expense_ald": "alimony_expense_ald_person",
}
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "above_the_line_deductions",
    *AGGREGATES,
    "loss_ald",
    "capped_qualified_tuition_expenses_ald",
    "taxable_ss_magi",
    "taxable_uc_agi",
    "tax_unit_taxable_social_security",
    "ma_gross_income",
    "ma_part_b_agi",
    "mn_homestead_credit_refund_household_income",
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
    *FILER_AMOUNTS,
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
        "qualified_tuition_expenses": draw(small),
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
        "state": draw(st.sampled_from(["TX", "MO", "MA", "MN"])),
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
        "qualified_tuition_expenses": some(7_000, 0.3),
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
                "state": str(rng.choice(["TX", "MO", "MA", "MN"])),
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
    np.testing.assert_allclose(
        run["alimony_expense_ald_person"],
        run["alimony_expense"] * (run["divorce_year"] < 2019),
        atol=TOLERANCE,
    )
    for aggregate, person_amount in AGGREGATES.items():
        np.testing.assert_allclose(
            run[aggregate],
            _unit_sum(run, filer * run[person_amount]),
            atol=TOLERANCE,
            err_msg=aggregate,
        )
    person_total = sum(run[name] for name in PERSON_DEDUCTIONS)
    filer_amounts = sum(run[name] for name in FILER_AMOUNTS)
    unit_level = run["loss_ald"] + run["capped_qualified_tuition_expenses_ald"]
    reference = unit_level + _unit_sum(run, filer * person_total + filer_amounts)
    np.testing.assert_allclose(
        run["above_the_line_deductions"], reference, atol=TOLERANCE
    )
    # Units without dependents: the previous all-member sum, unchanged.
    # Units with dependents: never more than it, and never negative.
    all_members = unit_level + _unit_sum(run, person_total + filer_amounts)
    assert (run["above_the_line_deductions"] >= -TOLERANCE).all()
    assert (run["above_the_line_deductions"] <= all_members + TOLERANCE).all()
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
    # Alimony a dependent pays under a pre-2019 instrument is one of their own
    # deductions too.
    own_person_deductions = person_total - run["student_loan_interest_ald"] + alimony
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


def _single_filer(year, state, **inputs):
    return {
        "people": {
            "filer": {
                "age": {year: 45},
                "employment_income": {year: 50_000},
                "is_tax_unit_head": {year: True},
            }
        },
        "tax_units": {
            "tax_unit": {
                "members": ["filer"],
                **{name: {year: value} for name, value in inputs.items()},
            }
        },
        "households": {
            "household": {"members": ["filer"], "state_code": {year: state}}
        },
    }


def test_person_splits_honor_tax_unit_inputs():
    # A tax-unit deduction supplied as an input still reaches the per-person
    # Medicaid AGI and the Mississippi adjustments, attributed to the head.
    sim = Simulation(
        situation=_single_filer(
            2025,
            "MS",
            alimony_expense_ald=3_000,
            self_employed_health_insurance_ald=200,
            self_employed_pension_contribution_ald=100,
        )
    )
    agi = sim.calculate("adjusted_gross_income", 2025)
    assert np.allclose(agi, 50_000 - 3_000 - 200 - 100)
    assert np.allclose(
        sim.calculate("medicaid_adjusted_gross_income_person", 2025), agi
    )
    assert np.allclose(
        sim.calculate("ms_self_employed_health_insurance_adjustment", 2025), 200
    )
    assert np.allclose(
        sim.calculate("ms_self_employed_retirement_adjustment", 2025), 100
    )


def test_person_splits_follow_the_deduction_list():
    # Removing alimony from gov.irs.ald.deductions removes it from both the
    # federal AGI and the Medicaid AGI built per person.
    from policyengine_core.periods import instant
    from policyengine_core.reforms import Reform

    class drop_alimony_deduction(Reform):
        def apply(self):
            def modify(parameters):
                node = parameters.gov.irs.ald.deductions
                start = instant("2025-01-01")
                kept = [d for d in node(start) if d != "alimony_expense_ald"]
                node.update(start=start, stop=instant("2025-12-31"), value=kept)
                return parameters

            self.modify_parameters(modify)

    situation = _single_filer(2025, "TX")
    situation["people"]["filer"].update(
        alimony_expense={2025: 1_000}, divorce_year={2025: 2010}
    )
    baseline = Simulation(situation=situation)
    assert np.allclose(baseline.calculate("adjusted_gross_income", 2025), 49_000)
    assert np.allclose(
        baseline.calculate("medicaid_adjusted_gross_income_person", 2025), 49_000
    )
    reformed = Simulation(situation=situation, reform=drop_alimony_deduction)
    assert np.allclose(reformed.calculate("adjusted_gross_income", 2025), 50_000)
    assert np.allclose(
        reformed.calculate("medicaid_adjusted_gross_income_person", 2025), 50_000
    )


def _ms_couple(premiums, **tax_unit_inputs):
    year = 2025
    return {
        "people": {
            "head": {
                "age": {year: 45},
                "is_tax_unit_head": {year: True},
                "employment_income": {year: 1_000},
            },
            "spouse": {
                "age": {year: 43},
                "is_tax_unit_spouse": {year: True},
                "self_employment_income": {year: 1_000},
                "self_employed_health_insurance_premiums": {year: premiums},
            },
        },
        "tax_units": {
            "tax_unit": {
                "members": ["head", "spouse"],
                **{name: {year: value} for name, value in tax_unit_inputs.items()},
            }
        },
        "marital_units": {"couple": {"members": ["head", "spouse"]}},
        "households": {
            "household": {"members": ["head", "spouse"], "state_code": {year: "MS"}}
        },
    }


SPLIT_OUTPUTS = [
    "ms_self_employed_health_insurance_adjustment",
    "ms_agi",
    "medicaid_adjusted_gross_income_person",
    "medicaid_magi_person",
    "medicaid_household_income",
    "adjusted_gross_income",
]


def _split_outputs(sim):
    return {name: np.asarray(sim.calculate(name, 2025)) for name in SPLIT_OUTPUTS}


@pytest.mark.parametrize("aggregate", [0, 500])
def test_reduced_tax_unit_amount_is_shared_without_negative_shares(aggregate):
    # A tax-unit deduction set below the spouse's own amount is shared in
    # proportion to the filers' own amounts, so no share turns negative and
    # the per-person floors in Mississippi AGI and Medicaid MAGI cannot add
    # income. The result equals a couple whose own amount is that deduction.
    reduced = Simulation(
        situation=_ms_couple(1_000, self_employed_health_insurance_ald=aggregate)
    )
    control = Simulation(situation=_ms_couple(aggregate))
    shares = reduced.calculate("ms_self_employed_health_insurance_adjustment", 2025)
    assert (np.asarray(shares) >= 0).all()
    assert np.allclose(shares, [0, aggregate])
    for name, values in _split_outputs(control).items():
        np.testing.assert_allclose(
            _split_outputs(reduced)[name], values, atol=TOLERANCE, err_msg=name
        )


def test_reformed_tax_unit_amount_is_shared_like_an_input():
    from policyengine_core.reforms import Reform

    from policyengine_us.model_api import TaxUnit, Variable

    class self_employed_health_insurance_ald(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = "year"

        def formula(tax_unit, period, parameters):
            return tax_unit.filled_array(0)

    class repeal_self_employed_health_insurance(Reform):
        def apply(self):
            self.update_variable(self_employed_health_insurance_ald)

    reformed = Simulation(
        situation=_ms_couple(1_000), reform=repeal_self_employed_health_insurance
    )
    control = Simulation(situation=_ms_couple(0))
    for name, values in _split_outputs(control).items():
        np.testing.assert_allclose(
            _split_outputs(reformed)[name], values, atol=TOLERANCE, err_msg=name
        )
