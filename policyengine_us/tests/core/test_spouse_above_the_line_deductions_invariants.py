"""Invariants for each spouse's own above-the-line deductions.

Each person's AGI (adjusted_gross_income_person) is their own gross income
less their own above-the-line deductions (above_the_line_deductions_person).
On a joint return a deduction that belongs to one spouse, such as their IRA
deduction, educator expenses, early withdrawal penalty, alimony paid, student
loan interest or business and capital losses, lowers only that spouse's AGI.
Only deductions recorded for the tax unit alone are divided equally. This
generator supplies HSA amounts only for the tax unit, so it exercises that
equal fallback; supplied person HSA amounts are attributed to their owners.
States that tax spouses
separately (Kentucky, Montana, Delaware, Virginia, Ohio's joint filing credit,
the District of Columbia, West Virginia's senior deduction) read these
amounts.

Hypothesis draws batches of tax units (single, joint, joint with dependents)
in those states, with every kind of deduction input, occasional business
losses over the Section 461(l) limit, and some tax-unit deductions
(loss_ald, alimony_expense_ald, self_employment_tax_ald) set directly; a
seeded population of 200 units adds breadth. Each batch runs as vectorized
simulations, once as drawn and once with the spouse's own deduction inputs set
to zero. Units that set the same tax-unit deduction directly share a
simulation, and units that set none share another: an input given for one
tax unit is an input for every unit in its simulation. For every tax unit:

1. Accounting identities. The head's and spouse's parts add up to the tax
   unit's amount: above_the_line_deductions_person to
   above_the_line_deductions, loss_ald_person to loss_ald,
   limited_capital_loss_person to limited_capital_loss and
   alimony_expense_ald_person to alimony_expense_ald. The members'
   adjusted_gross_income_person add up to adjusted_gross_income, and so do
   the head's and spouse's Medicaid AGIs. This holds when a tax-unit
   deduction is set directly too, except that alimony_expense_ald_person
   stays each payer's own alimony when alimony_expense_ald is set directly
   (above_the_line_deductions_person divides the difference).
2. Differential. limited_business_loss and limited_capital_loss equal numpy
   computations of the Section 461(l) and 1211(b) limits from the inputs and
   parameters. For units with no deduction set directly,
   above_the_line_deductions_person equals a numpy reference built from the
   inputs: each person's own person-level deductions, their alimony under a
   pre-2019 instrument, their share of the numpy-limited business loss by
   their own business losses and of the capital loss deduction (losses up
   to the filers' capital gains and distributions, plus the net loss up to
   the 1211(b) limit) by their own capital losses, and an equal share of the
   HSA and tuition and fees deductions.
3. Own deductions. The spouse's deductions never add to the head's: the
   head's above_the_line_deductions_person is never higher with the spouse's
   deduction inputs than without them. It is the same, and so is the head's
   AGI, when the head has no loss or student loan interest that shares a
   return-level limit with the spouse's, and no income (Social Security,
   unemployment compensation) taxed by reference to the couple's AGI. The
   spouse's own AGI and the couple's AGI never fall when the spouse's
   deduction inputs are removed.
   This is checked for units with no deduction set directly.
4. Dependents. A dependent's adjusted_gross_income_person, loss_ald_person
   and limited_capital_loss_person are zero, and their
   above_the_line_deductions_person is their own person-level deductions.
5. Bounds. Every above_the_line_deductions_person and loss_ald_person is
   non-negative.
6. DC separate filing on the same return. For the head and spouse of a joint
   DC return, dc_separate_capital_loss_adjustment equals the capital part of
   their loss_ald_person (loss_ald less the business loss, by their own
   capital losses) less their own capital losses up to their own capital
   gains and distributions plus the $1,500 separate limit; it is zero for
   everyone else. For units with no deduction set directly, that capital part
   equals the numpy capital loss deduction, and each couple's adjustments add
   up to zero or more: filing separately never deducts more capital loss than
   the joint return. (A loss_ald set directly below the losses can make the
   sum negative.)
   (The YAML tests check that the joint DC computation is unaffected.)
7. Montana from 2024. Spouses no longer file separately on the same form, so
   mt_loss_ald_reallocation and mt_applicable_ald_deductions are zero.
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
# Tax-unit deductions that a unit may set directly.
DIRECT_INPUTS = ["loss_ald", "alimony_expense_ald", "self_employment_tax_ald"]
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "above_the_line_deductions",
    "loss_ald",
    "limited_business_loss",
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
    "irs_gross_income",
    "capital_losses",
    "capital_gains",
    "non_sch_d_capital_gains",
    "alimony_expense",
    "divorce_year",
    "student_loan_interest",
    "social_security",
    "unemployment_compensation",
    "dc_separate_capital_loss_adjustment",
    "mt_loss_ald_reallocation",
    "mt_applicable_ald_deductions",
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
        "direct": draw(
            st.one_of(
                st.none(),
                st.tuples(
                    st.sampled_from(DIRECT_INPUTS),
                    st.integers(0, 8_000).map(float),
                ),
            )
        ),
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
                "direct": (
                    (
                        str(rng.choice(DIRECT_INPUTS)),
                        float(round(rng.uniform(0, 8_000))),
                    )
                    if rng.random() < 0.15
                    else None
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
        if u["direct"] is not None:
            name, value = u["direct"]
            groups["tax_units"][f"tax_unit_{i}"][name] = {year: value}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: u["state"]},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _direct_name(unit):
    return unit["direct"][0] if unit["direct"] is not None else ""


def _grouped(units):
    """The units ordered so those setting the same variable directly are together.

    A variable given as an input for one tax unit becomes an input for every
    tax unit in the simulation, at its default value for the others, so a
    loss_ald set directly for one unit would set every other unit's loss_ald
    to zero. Each group therefore runs as its own simulation.
    """
    names = sorted({_direct_name(u) for u in units})
    return [[u for u in units if _direct_name(u) == name] for name in names]


def _run(units, year, *, zero_spouse):
    """Run each group of _grouped(units) and join the results in that order."""
    runs = [
        _run_group(group, year, zero_spouse=zero_spouse) for group in _grouped(units)
    ]
    offset = 0
    for run in runs:
        run["unit"] = run["unit"] + offset
        offset += len(run["adjusted_gross_income"])
    return {key: np.concatenate([run[key] for run in runs]) for key in runs[0]}


def _run_group(units, year, *, zero_spouse):
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
        elif deduction == "health_savings_account_ald":
            # These generators supply only the return's HSA amount. With
            # no person amounts, the existing equal fallback still applies
            # even though main now provides an optional *_person input.
            shared_names.append(deduction)
        elif f"{deduction}_person" in tbs.variables:
            own_names.append(f"{deduction}_person")
        else:
            shared_names.append(deduction)
    # Amounts that are the filer's even when recorded on a dependent.
    out["filer_amounts"] = sum(
        (
            np.asarray(sim.calculate(name, year), dtype=float)
            for name in tbs.parameters(
                f"{year}-01-01"
            ).gov.irs.ald.filer_amounts_recorded_on_dependents
        ),
        np.zeros(len(out["adjusted_gross_income_person"])),
    )
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
    # The Section 461(l) and 1211(b) limits for each unit's filing status.
    filing_status = sim.calculate("filing_status", year).decode_to_str()
    loss = tbs.parameters(f"{year}-01-01").gov.irs.ald.loss
    out["business_loss_limit"] = np.asarray(loss.max[filing_status], dtype=float)
    out["capital_loss_limit"] = np.asarray(loss.capital.max[filing_status], dtype=float)
    out["separate_capital_loss_limit"] = np.full(
        len(filing_status), float(loss.capital.max["SEPARATE"])
    )
    out["joint"] = filing_status == "JOINT"
    out["state"] = np.array([u["state"] for u in units])
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


def _limits(run):
    """The limited business and capital losses of each unit, with numpy."""
    filer = ~run["is_dependent"]
    # Section 461(l)(3)(A) compares the aggregate deductions of the trades or
    # businesses with their aggregate gross income or gain, so each source's
    # gain and loss count separately, not netted for the person first.
    gains = sum(np.maximum(0, run[source]) for source in BUSINESS_SOURCES)
    losses = sum(np.maximum(0, -run[source]) for source in BUSINESS_SOURCES)
    other_net_gain = run["other_net_gain"]
    income = _unit_sum(run, filer * gains) + np.maximum(0, other_net_gain)
    loss = _unit_sum(run, filer * losses) + np.maximum(0, -other_net_gain)
    limited_business = np.minimum(loss, income + run["business_loss_limit"])
    # 26 USC 1211(b): capital losses are allowed to the extent of capital
    # gains, each filer's net gain and capital gain distributions (Schedule D
    # lines 13 and 16), plus a net loss up to the limit (line 21).
    capital_losses = _unit_sum(run, filer * run["capital_losses"])
    capital_gains = _unit_sum(
        run,
        filer
        * (
            np.maximum(0, run["capital_gains"])
            + np.maximum(0, run["non_sch_d_capital_gains"])
        ),
    )
    allowed_against_gains = np.minimum(capital_losses, capital_gains)
    limited_capital = np.minimum(
        run["capital_loss_limit"], capital_losses - allowed_against_gains
    )
    return limited_business, limited_capital, allowed_against_gains


def _even(run):
    """An equal share for each filer of a unit."""
    filer = ~run["is_dependent"]
    filers = _per_person(run, _unit_sum(run, filer.astype(float)))
    return np.divide(
        filer.astype(float), filers, out=np.zeros_like(filers), where=filers > 0
    )


def _capital_deduction_person(run):
    """Each filer's share of the capital loss deduction, by their own losses."""
    capital_loss = ~run["is_dependent"] * run["capital_losses"]
    _, limited_capital, allowed_against_gains = _limits(run)
    capital_deduction = _per_person(run, allowed_against_gains + limited_capital)
    return capital_deduction * _share(
        capital_loss, _per_person(run, _unit_sum(run, capital_loss)), _even(run)
    )


def _capital_part_of_loss_ald(run):
    """Each filer's share of loss_ald less the business loss, by own losses."""
    business_part = np.minimum(run["limited_business_loss"], run["loss_ald"])
    capital_part = np.maximum(0, run["loss_ald"] - business_part)
    capital_loss = ~run["is_dependent"] * run["capital_losses"]
    return _per_person(run, capital_part) * _share(
        capital_loss, _per_person(run, _unit_sum(run, capital_loss)), _even(run)
    )


def _reference(run):
    """above_the_line_deductions_person, built from the inputs with numpy."""
    filer = ~run["is_dependent"]
    even = _even(run)
    business_loss = filer * sum(
        np.maximum(0, -run[source]) for source in BUSINESS_SOURCES
    )
    business_loss = business_loss + even * np.maximum(
        0, -_per_person(run, run["other_net_gain"])
    )
    limited_business, _, _ = _limits(run)
    limited_business = _per_person(run, limited_business)
    losses = limited_business * _share(
        business_loss, _per_person(run, _unit_sum(run, business_loss)), even
    ) + _capital_deduction_person(run)
    alimony = run["alimony_expense"] * (run["divorce_year"] < 2019)
    # Tax-unit deductions with no person amounts are divided equally.
    shared = _per_person(run, run["shared"]) * even
    # A filer amount recorded on a dependent (gov.irs.ald.
    # filer_amounts_recorded_on_dependents) is not on the dependent's own
    # return; the head and spouse divide it equally.
    dependent_filer_amounts = _per_person(
        run, _unit_sum(run, run["is_dependent"] * run["filer_amounts"])
    )
    filer_part = run["own_direct"] + alimony + losses + shared
    filer_part = filer_part + dependent_filer_amounts * even
    return np.where(
        filer,
        filer_part,
        run["own_direct"] + alimony - run["filer_amounts"],
    )


def _close(actual, desired, **kwargs):
    np.testing.assert_allclose(actual, desired, atol=TOLERANCE, rtol=RTOL, **kwargs)


def _at_most(lower, upper):
    return (lower <= upper + TOLERANCE + RTOL * np.abs(upper)).all()


def _check(units, year):
    # The order in which _run returns the units.
    units = [u for group in _grouped(units) for u in group]
    run = _run(units, year, zero_spouse=False)
    zeroed = _run(units, year, zero_spouse=True)
    filer = ~run["is_dependent"]
    dependent = run["is_dependent"]
    direct_unit = np.array([u["direct"] is not None for u in units])
    direct = _per_person(run, direct_unit)

    # 1. Accounting identities.
    pairs = [
        ("above_the_line_deductions_person", "above_the_line_deductions"),
        ("loss_ald_person", "loss_ald"),
        ("limited_capital_loss_person", "limited_capital_loss"),
        ("alimony_expense_ald_person", "alimony_expense_ald"),
    ]
    set_directly = np.array([_direct_name(u) for u in units])
    for person_name, unit_name in pairs:
        # alimony_expense_ald_person is each payer's own alimony, so it adds up
        # to alimony_expense_ald unless that is set directly;
        # above_the_line_deductions_person reconciles the difference.
        kept = (unit_name != "alimony_expense_ald") | (set_directly != unit_name)
        _close(
            _unit_sum(run, filer * run[person_name])[kept],
            run[unit_name][kept],
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

    # 2. Differential against numpy.
    limited_business, limited_capital, _ = _limits(run)
    _close(run["limited_business_loss"], limited_business)
    _close(run["limited_capital_loss"], limited_capital)
    _close(run["above_the_line_deductions_person"][~direct], _reference(run)[~direct])

    # 3. The spouse's deductions never add to the head's. A head with student
    # loan interest is left out of the first check: the spouse's IRA
    # deduction, for example, lowers the couple's MAGI and with it the
    # phase-out of the head's student loan interest deduction.
    head = run["is_head"]
    spouse = run["is_spouse"]
    has_spouse = _per_person(run, _unit_sum(run, spouse.astype(float))) > 0
    paired_head = head & has_spouse & ~direct
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
    assert _at_most(run[agi][spouse & ~direct], zeroed[agi][spouse & ~direct])
    assert _at_most(
        run["adjusted_gross_income"][~direct_unit],
        zeroed["adjusted_gross_income"][~direct_unit],
    )

    # 4. Dependents.
    for name in ["adjusted_gross_income_person", "loss_ald_person"]:
        assert (run[name][dependent] == 0).all(), name
    assert (run["limited_capital_loss_person"][dependent] == 0).all()

    # 5. Bounds.
    for name in ["above_the_line_deductions_person", "loss_ald_person"]:
        assert (run[name] >= -TOLERANCE).all(), name

    # 6. DC separate filing on the same return.
    adjustment = run["dc_separate_capital_loss_adjustment"]
    dc_unit = run["state"] == "DC"
    dc_joint = _per_person(run, dc_unit & run["joint"]) & (head | spouse)
    own_gains = np.maximum(0, run["capital_gains"]) + np.maximum(
        0, run["non_sch_d_capital_gains"]
    )
    separate = np.minimum(
        run["capital_losses"],
        own_gains + _per_person(run, run["separate_capital_loss_limit"]),
    )
    # The capital part of each filer's loss_ald_person, which their federal
    # AGI includes. For units with no deduction set directly it is the numpy
    # capital loss deduction.
    federal = _capital_part_of_loss_ald(run)
    _close(federal[~direct], _capital_deduction_person(run)[~direct])
    _close(adjustment, dc_joint * (federal - separate))
    assert (adjustment[~dc_joint] == 0).all()
    # A loss_ald set directly below the capital losses can leave the separate
    # columns deducting more than federal AGI does.
    assert (_unit_sum(run, adjustment)[~direct_unit] >= -TOLERANCE).all()

    # 7. Montana from 2024.
    if year >= 2024:
        for name in ["mt_loss_ald_reallocation", "mt_applicable_ald_deductions"]:
            assert (run[name] == 0).all(), name


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
    # purposes file separately on the same form, a path that reads each
    # spouse's AGI.
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
    # A tax-unit deduction with no person-level variable falls back to an equal
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
