"""Invariants for each spouse's own above-the-line deductions.

Each person's AGI (adjusted_gross_income_person) is their own gross income
less their own above-the-line deductions (above_the_line_deductions_person).
On a joint return a deduction that belongs to one spouse, such as their IRA
deduction, educator expenses, early withdrawal penalty, alimony paid, student
loan interest or business and capital losses, lowers only that spouse's AGI.
Only deductions recorded for the tax unit alone (here the HSA deduction and
the tuition and fees deduction) are divided equally. States that tax spouses
separately (Kentucky, Montana, Delaware, Virginia, Ohio's joint filing credit,
the District of Columbia, West Virginia's senior deduction) read these
amounts.

Hypothesis draws batches of tax units (single, joint, joint with dependents)
in those states, with every kind of deduction input and occasional business
losses over the Section 461(l) limit; a seeded population of 200 units adds
breadth. Each batch runs as one vectorized simulation, once as drawn and once
with the spouse's own deduction inputs set to zero. For every tax unit:

1. Accounting identities. The head's and spouse's parts add up to the tax
   unit's amount: above_the_line_deductions_person to
   above_the_line_deductions, loss_ald_person to loss_ald,
   limited_capital_loss_person to limited_capital_loss and
   alimony_expense_ald_person to alimony_expense_ald. The members'
   adjusted_gross_income_person add up to adjusted_gross_income, and so do
   the head's and spouse's Medicaid AGIs. Montana's capital loss
   reallocation adds up to zero.
2. Differential. above_the_line_deductions_person equals an independent numpy
   reference built from the inputs: each person's own person-level
   deductions, their alimony under a pre-2019 instrument, their share of the
   limited business loss by their own business losses and of the limited
   capital loss by their own capital losses, and an equal share of the HSA
   and tuition and fees deductions.
3. Own deductions. The spouse's deductions never add to the head's: the
   head's above_the_line_deductions_person is never higher with the spouse's
   deduction inputs than without them. It is the same, and so is the head's
   AGI, when the head has no loss or student loan interest that shares a
   return-level limit with the spouse's, and no income (Social Security,
   unemployment compensation) taxed by reference to the couple's AGI. The
   spouse's own AGI and the couple's AGI never fall when the spouse's
   deduction inputs are removed.
4. Dependents. A dependent's adjusted_gross_income_person, loss_ald_person
   and limited_capital_loss_person are zero, and their
   above_the_line_deductions_person is their own person-level deductions.
5. Bounds. Every above_the_line_deductions_person is non-negative.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# Values are float32, and a business loss over the Section 461(l) limit puts
# AGI in the millions, so allow a relative error as well as cents.
TOLERANCE = 0.05  # dollars
RTOL = 2e-6

STATES = ["KY", "MT", "DE", "VA", "OH", "DC", "WV"]

# A person's inputs behind deductions that belong to them.
OWN_DEDUCTION_INPUTS = [
    "traditional_ira_contributions",
    "early_withdrawal_penalty",
    "educator_expense",
    "alimony_expense",
    "qualified_adoption_assistance_expense",
    "us_bonds_for_higher_ed",
    "student_loan_interest",
    "self_employed_health_insurance_premiums",
    "self_employed_pension_contributions",
]
# Inputs whose negative values are losses.
LOSS_INPUTS = [
    "self_employment_income",
    "rental_income",
    "long_term_capital_gains",
    "short_term_capital_gains",
]
BUSINESS_SOURCES = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "above_the_line_deductions",
    "loss_ald",
    "limited_capital_loss",
    "alimony_expense_ald",
    "health_savings_account_ald",
    "other_net_gain",
]
PERSON_OUTPUTS = [
    "above_the_line_deductions_person",
    "adjusted_gross_income_person",
    "medicaid_adjusted_gross_income_person",
    "loss_ald_person",
    "limited_capital_loss_person",
    "alimony_expense_ald_person",
    "mt_capital_loss_reallocation",
    "irs_gross_income",
    "capital_losses",
    "alimony_expense",
    "divorce_year",
    "student_loan_interest",
    "social_security",
    "unemployment_compensation",
    *BUSINESS_SOURCES,
]

amount = st.integers(1, 40_000).map(float)
small = st.one_of(st.just(0.0), st.integers(1, 7_000).map(float))


def _maybe(draw, strategy):
    return draw(st.one_of(st.just(0.0), strategy))


@st.composite
def person_amounts(draw, *, dependent):
    big_loss = draw(st.integers(0, 19)) == 0
    return {
        "employment_income": _maybe(draw, amount),
        "self_employment_income": (
            -1_500_000.0
            if big_loss
            else _maybe(draw, st.integers(-20_000, 60_000).map(float))
        ),
        "rental_income": _maybe(draw, st.integers(-15_000, 20_000).map(float)),
        "long_term_capital_gains": _maybe(
            draw, st.integers(-15_000, 15_000).map(float)
        ),
        "short_term_capital_gains": _maybe(draw, st.integers(-5_000, 5_000).map(float)),
        "taxable_interest_income": _maybe(draw, st.integers(1, 2_000).map(float)),
        "traditional_ira_contributions": draw(small),
        "early_withdrawal_penalty": draw(st.integers(0, 500).map(float)),
        "educator_expense": draw(st.integers(0, 400).map(float)),
        "alimony_expense": draw(small),
        "divorce_year": draw(st.sampled_from([2010, 2018, 2020])),
        "qualified_adoption_assistance_expense": draw(small),
        "us_bonds_for_higher_ed": draw(small),
        "student_loan_interest": _maybe(draw, st.integers(1, 3_500).map(float)),
        "self_employed_health_insurance_premiums": draw(small),
        "self_employed_pension_contributions": draw(small),
        "social_security_retirement": (0.0 if dependent else _maybe(draw, amount)),
        "unemployment_compensation": _maybe(draw, st.integers(1, 15_000).map(float)),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "joint", "joint_dependents"]))
    return {
        "state": draw(st.sampled_from(STATES)),
        "health_savings_account_ald": _maybe(draw, st.integers(1, 8_000).map(float)),
        "other_net_gain": _maybe(draw, st.integers(-5_000, 5_000).map(float)),
        "head": draw(person_amounts(dependent=False)),
        "spouse": (draw(person_amounts(dependent=False)) if kind != "single" else None),
        "dependents": [
            {"age": draw(st.integers(5, 23)), **draw(person_amounts(dependent=True))}
            for _ in range(draw(st.integers(1, 2)) if kind == "joint_dependents" else 0)
        ],
    }


SEED = 20261006


def _seeded_amounts(rng, *, dependent):
    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    return {
        "employment_income": some(1, 40_000, 0.6),
        "self_employment_income": (
            -1_500_000.0 if rng.random() < 0.05 else some(-20_000, 60_000, 0.6)
        ),
        "rental_income": some(-15_000, 20_000, 0.3),
        "long_term_capital_gains": some(-15_000, 15_000, 0.4),
        "short_term_capital_gains": some(-5_000, 5_000, 0.3),
        "taxable_interest_income": some(1, 2_000),
        "traditional_ira_contributions": some(1, 7_000),
        "early_withdrawal_penalty": some(1, 500),
        "educator_expense": some(1, 400),
        "alimony_expense": some(1, 7_000, 0.3),
        "divorce_year": int(rng.choice([2010, 2018, 2020])),
        "qualified_adoption_assistance_expense": some(1, 7_000, 0.2),
        "us_bonds_for_higher_ed": some(1, 7_000, 0.2),
        "student_loan_interest": some(1, 3_500, 0.4),
        "self_employed_health_insurance_premiums": some(1, 7_000, 0.3),
        "self_employed_pension_contributions": some(1, 7_000, 0.3),
        "social_security_retirement": 0.0 if dependent else some(1, 40_000, 0.3),
        "unemployment_compensation": some(1, 15_000, 0.2),
    }


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "joint", "joint_dependents"])
        units.append(
            {
                "state": str(rng.choice(STATES)),
                "health_savings_account_ald": (
                    float(round(rng.uniform(1, 8_000))) if rng.random() < 0.3 else 0.0
                ),
                "other_net_gain": (
                    float(round(rng.uniform(-5_000, 5_000)))
                    if rng.random() < 0.2
                    else 0.0
                ),
                "head": _seeded_amounts(rng, dependent=False),
                "spouse": (
                    _seeded_amounts(rng, dependent=False) if kind != "single" else None
                ),
                "dependents": [
                    {
                        "age": int(rng.integers(5, 24)),
                        **_seeded_amounts(rng, dependent=True),
                    }
                    for _ in range(
                        int(rng.integers(1, 3)) if kind == "joint_dependents" else 0
                    )
                ],
            }
        )
    return units


def _zero_own_deductions(amounts):
    zeroed = {**amounts, **{name: 0.0 for name in OWN_DEDUCTION_INPUTS}}
    for name in LOSS_INPUTS:
        zeroed[name] = max(0.0, zeroed[name])
    return zeroed


def _situation(units, year, *, zero_spouse):
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
            amounts = u["spouse"]
            if zero_spouse:
                amounts = _zero_own_deductions(amounts)
            people[spouse] = {
                "age": 48,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **amounts,
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            people[child] = {
                "age": d["age"],
                "is_full_time_student": d["age"] >= 19,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
                **{k: v for k, v in d.items() if k != "age"},
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "health_savings_account_ald": {year: u["health_savings_account_ald"]},
            "other_net_gain": {year: u["other_net_gain"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: u["state"]},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, zero_spouse):
    sim = Simulation(situation=_situation(units, year, zero_spouse=zero_spouse))
    tbs = sim.tax_benefit_system
    deductions = tbs.parameters(f"{year}-01-01").gov.irs.ald.deductions
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in TAX_UNIT_OUTPUTS + PERSON_OUTPUTS
    }
    # The person-level deductions and the person amounts behind the tax-unit
    # deductions other than losses and alimony, which the reference below
    # builds from the inputs.
    own_names, shared_names = [], []
    for deduction in sorted(set(deductions)):
        if tbs.variables[deduction].entity.is_person:
            own_names.append(deduction)
        elif deduction in ("loss_ald", "alimony_expense_ald"):
            continue
        elif f"{deduction}_person" in tbs.variables:
            own_names.append(f"{deduction}_person")
        else:
            shared_names.append(deduction)
    out["own_direct"] = sum(
        np.asarray(sim.calculate(name, year), dtype=float) for name in own_names
    )
    out["shared"] = sum(
        (np.asarray(sim.calculate(name, year), dtype=float) for name in shared_names),
        np.zeros(len(out["adjusted_gross_income"])),
    )
    out["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    out["is_head"] = np.asarray(sim.calculate("is_tax_unit_head", year), dtype=bool)
    out["is_spouse"] = np.asarray(sim.calculate("is_tax_unit_spouse", year), dtype=bool)
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(run, values):
    return np.bincount(
        run["unit"], weights=values, minlength=len(run["adjusted_gross_income"])
    )


def _per_person(run, unit_values):
    return np.asarray(unit_values)[run["unit"]]


def _share(amounts, totals, fallback):
    return np.where(
        totals > 0,
        np.divide(amounts, totals, out=np.zeros_like(amounts), where=totals > 0),
        fallback,
    )


def _reference(run):
    """above_the_line_deductions_person, built from the inputs with numpy."""
    filer = ~run["is_dependent"]
    filers = _per_person(run, _unit_sum(run, filer.astype(float)))
    even = np.divide(
        filer.astype(float), filers, out=np.zeros_like(filers), where=filers > 0
    )
    business_loss = filer * sum(
        np.maximum(0, -run[source]) for source in BUSINESS_SOURCES
    )
    business_loss = business_loss + even * np.maximum(
        0, -_per_person(run, run["other_net_gain"])
    )
    capital_loss = filer * run["capital_losses"]
    limited_capital = _per_person(run, run["limited_capital_loss"])
    limited_business = np.maximum(
        0, _per_person(run, run["loss_ald"]) - limited_capital
    )
    losses = limited_business * _share(
        business_loss, _per_person(run, _unit_sum(run, business_loss)), even
    ) + limited_capital * _share(
        capital_loss, _per_person(run, _unit_sum(run, capital_loss)), even
    )
    alimony = run["alimony_expense"] * (run["divorce_year"] < 2019)
    # Tax-unit deductions with no person amounts are divided equally.
    shared = _per_person(run, run["shared"]) * even
    return np.where(
        filer,
        run["own_direct"] + alimony + losses + shared,
        run["own_direct"] + alimony,
    )


def _close(actual, desired, **kwargs):
    np.testing.assert_allclose(actual, desired, atol=TOLERANCE, rtol=RTOL, **kwargs)


def _at_most(lower, upper):
    return (lower <= upper + TOLERANCE + RTOL * np.abs(upper)).all()


def _check(units, year):
    run = _run(units, year, zero_spouse=False)
    zeroed = _run(units, year, zero_spouse=True)
    filer = ~run["is_dependent"]
    dependent = run["is_dependent"]

    # 1. Accounting identities.
    pairs = [
        ("above_the_line_deductions_person", "above_the_line_deductions"),
        ("loss_ald_person", "loss_ald"),
        ("limited_capital_loss_person", "limited_capital_loss"),
        ("alimony_expense_ald_person", "alimony_expense_ald"),
    ]
    for person_name, unit_name in pairs:
        _close(
            _unit_sum(run, filer * run[person_name]),
            run[unit_name],
            err_msg=person_name,
        )
    _close(
        _unit_sum(run, run["adjusted_gross_income_person"]),
        run["adjusted_gross_income"],
    )
    _close(
        _unit_sum(run, filer * run["medicaid_adjusted_gross_income_person"]),
        run["adjusted_gross_income"],
    )
    _close(_unit_sum(run, run["mt_capital_loss_reallocation"]), 0)

    # 2. Differential against the numpy reference.
    _close(run["above_the_line_deductions_person"], _reference(run))

    # 3. The spouse's deductions never add to the head's. A head with student
    # loan interest is left out of the first check: the spouse's IRA
    # deduction, for example, lowers the couple's MAGI and with it the
    # phase-out of the head's student loan interest deduction.
    head = run["is_head"]
    spouse = run["is_spouse"]
    has_spouse = _per_person(run, _unit_sum(run, spouse.astype(float))) > 0
    paired_head = head & has_spouse
    # Each filer's deductions as their AGI shows them.
    deductions = "deductions_in_agi"
    for r in (run, zeroed):
        r[deductions] = r["irs_gross_income"] - r["adjusted_gross_income_person"]
    agi = "adjusted_gross_income_person"
    no_student_loan = run["student_loan_interest"] == 0
    checked = paired_head & no_student_loan
    assert _at_most(run[deductions][checked], zeroed[deductions][checked])
    # A Form 4797 loss, recorded for the tax unit, is a business loss of both
    # the head and spouse.
    has_loss = (
        (run["capital_losses"] > 0)
        | (sum(np.maximum(0, -run[source]) for source in BUSINESS_SOURCES) > 0)
        | (_per_person(run, run["other_net_gain"]) < 0)
    )
    own_only = checked & ~has_loss
    _close(run[deductions][own_only], zeroed[deductions][own_only])
    joint_taxed_income = (run["social_security"] > 0) | (
        run["unemployment_compensation"] > 0
    )
    unaffected = own_only & ~joint_taxed_income
    _close(run[agi][unaffected], zeroed[agi][unaffected])
    assert _at_most(run[agi][spouse], zeroed[agi][spouse])
    assert _at_most(run["adjusted_gross_income"], zeroed["adjusted_gross_income"])

    # 4. Dependents.
    for name in ["adjusted_gross_income_person", "loss_ald_person"]:
        assert (run[name][dependent] == 0).all(), name
    assert (run["limited_capital_loss_person"][dependent] == 0).all()

    # 5. Bounds.
    assert (run["above_the_line_deductions_person"] >= -TOLERANCE).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_own_deductions_2026(units):
    _check(units, 2026)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_own_deductions_2023(units):
    # 2023 is the last year Montana lets spouses who file jointly for federal
    # purposes file separately on the same form, the path that reads each
    # spouse's AGI and the Montana capital loss reallocation.
    _check(units, 2023)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_own_deductions_2020(units):
    # 2020 adds the tuition and fees deduction, divided equally, and the
    # unemployment compensation exclusion, which reads the couple's AGI.
    _check(units, 2020)


@pytest.mark.parametrize("year", [2020, 2023, 2026])
def test_seeded_population(year):
    _check(_seeded_units(), year)


def test_every_deduction_is_attributed_or_divided_equally_on_purpose():
    # A tax-unit deduction with no person amount falls back to an equal
    # division between the head and spouse. Only those listed, with their
    # reasons, in EQUALLY_DIVIDED_DEDUCTIONS may do so.
    from policyengine_us import CountryTaxBenefitSystem
    from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.above_the_line_deductions_person import (
        EQUALLY_DIVIDED_DEDUCTIONS,
    )

    system = CountryTaxBenefitSystem()
    deductions = system.parameters.gov.irs.ald.deductions
    seen = set()
    for value in deductions.values_list:
        seen.update(deductions(value.instant_str))
    for deduction in sorted(seen):
        variable = system.variables[deduction]
        attributed = (
            variable.entity.is_person or f"{deduction}_person" in system.variables
        )
        assert attributed != (deduction in EQUALLY_DIVIDED_DEDUCTIONS), deduction
