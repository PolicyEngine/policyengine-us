"""Invariants for a tax unit dependent's retirement income in state income tax.

`irs_gross_income` leaves out every tax unit dependent's income: a dependent
reports it on their own return, and 26 USC 1(g)(7) can move only a child's
interest and dividends to a parent's return. State income taxes that start
from federal AGI therefore must not subtract a dependent's pension, IRA or
401(k) distributions, military retirement pay or survivor benefits from the
filer's income.

The tests draw a seeded random population of tax units and run each scenario
as one vectorized simulation. Each unit is single or joint, with wages,
retirement income and Social Security for the head and spouse, who are aged
from 35 to 80: under and over the common retirement-exclusion ages, and over
the ages that gate credits such as Utah's retirement credit (born in 1952 or
earlier). The filers' incomes are drawn at full or at a quarter scale, so
units fall both above and below the limits on income-tested credits and
exclusions. Each unit has zero to two dependents, either children or an
elderly relative. Social Security, moderate incomes and the older ages all
matter: Utah's military retirement credit, for example, is open only when
the income-limited Social Security credit outweighs the age-gated retirement
credit, and Pennsylvania excludes retirement income only past age 59.5.
Each person also draws a military record: retired after 20 years, retired
early, medically retired, the Survivor Benefit Plan beneficiary of a member
who qualified for North Carolina's deduction, or none of these.
Two fixed joint households replace random draws to guarantee mixed military
eligibility and a civilian qualifying survivor in both test years.

1. `tax_unit_non_dep_add` equals a numpy reference: the head's and spouse's
   amounts of person-level variables plus tax-unit-level variables. For tax
   units without dependents it equals `add`.
2. Outside STATES_WITH_INTENDED_RETIREMENT_TAX_DECREASES, giving the
   dependents retirement income never lowers the filer's state income tax.
   Michigan is an intended exception: a dependent adult's pension can lower
   their SSI and increase the claimant's refundable credit. Outside
   STATES_COUNTING_DEPENDENT_INCOME it changes neither the state AGI nor the
   state taxable income. (State income tax itself may still rise: credits
   keyed to household income, such as Oklahoma's sales tax relief credit,
   count every household member's income.) Michigan's pension benefits,
   subtractions and tax before refundable credits must remain unchanged.
3. A unit whose dependents have no income has the same inputs in both
   populations, so its state income tax, AGI and taxable income are the same
   in both: no unit's results depend on another unit's inputs.
4. North Carolina's military retirement deduction is the head's and spouse's
   qualifying pay, each judged on their own record: their retirement pay if
   they served 20 years or were medically retired, and Survivor Benefit Plan
   payments if the deceased member did (G.S. 105-153.5(b)(5a)).
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.model_api import add, tax_unit_non_dep_add
from policyengine_core.periods import period as make_period

SEED = 20260928
TOLERANCE = 0.01  # dollars

# Ages that reach every retirement age test, including Utah's retirement
# credit (born in 1952 or earlier, so 73 or older in 2025).
FILER_AGES = [35, 60, 67, 70, 75, 80]
# Most units draw incomes well above the limits on income-tested credits and
# exclusions (Utah's Social Security credit phases out above $75,000 of
# modified AGI for a single filer, for example), so a unit's filer income is
# scaled by one of these.
FILER_INCOME_SCALES = [0.25, 1.0]
# The share of dependents who are an elderly qualifying relative, such as a
# parent, rather than a child. A qualifying relative's gross income must stay
# under the exemption amount ($5,200 in 2025), so their draws are kept small.
ELDERLY_DEPENDENT_SHARE = 1 / 3
ELDERLY_DEPENDENT_SCALE = 800
RETIREMENT_INPUTS = [
    "taxable_public_pension_income",
    "taxable_private_pension_income",
    "military_retirement_pay",
    "military_retirement_pay_survivors",
    "pension_survivors",
    "taxable_ira_distributions",
    "taxable_401k_distributions",
    "taxable_403b_distributions",
]

# Military records, drawn for every person. North Carolina deducts the
# retirement pay of a member who served 20 years or was medically retired, and
# Survivor Benefit Plan payments to the beneficiary of such a member.
NC_MINIMUM_SERVICE_YEARS = 20
MILITARY_RECORDS = [
    # Retired after 20 or more years.
    {"years": 22, "medically_retired": False, "nc_survivor": False},
    # Retired early, without 20 years or a medical retirement.
    {"years": 15, "medically_retired": False, "nc_survivor": False},
    # Medically retired.
    {"years": 8, "medically_retired": True, "nc_survivor": False},
    # The Survivor Benefit Plan beneficiary of a member who qualified.
    {"years": 0, "medically_retired": False, "nc_survivor": True},
    # No service, or survivor benefits from a member who did not qualify.
    {"years": 0, "medically_retired": False, "nc_survivor": False},
]


def _draw_military(rng):
    return MILITARY_RECORDS[int(rng.integers(len(MILITARY_RECORDS)))]


def _military_inputs(record, year):
    return {
        "years_in_military": {year: record["years"]},
        "is_permanently_disabled_veteran": {year: record["medically_retired"]},
        "nc_military_retirement_survivor_eligible": {year: record["nc_survivor"]},
    }


def _draw_units(n, rng):
    units = []
    for _ in range(n):
        joint = bool(rng.random() < 0.5)
        n_dependents = int(rng.integers(0, 3))
        # Scale the filers' income down in some units, so the draws reach the
        # moderate incomes that income-limited credits and exclusions need.
        income_scale = float(rng.choice(FILER_INCOME_SCALES))

        def draw(scale):
            return float(round(rng.choice([0.0, rng.uniform(0, scale)])))

        def retirement(scale):
            return {name: draw(scale) for name in RETIREMENT_INPUTS}

        def filer():
            return {
                **retirement(40_000 * income_scale),
                "social_security": draw(40_000 * income_scale),
            }

        def dependent():
            if rng.random() < ELDERLY_DEPENDENT_SHARE:
                # A qualifying relative, such as an elderly parent.
                return {
                    "age": int(rng.choice([70, 78, 85])),
                    "income": retirement(ELDERLY_DEPENDENT_SCALE),
                }
            # A qualifying child (under 19), so no dependency test turns on
            # the child's own income.
            return {"age": int(rng.integers(1, 19)), "income": retirement(15_000)}

        units.append(
            {
                "joint": joint,
                "head_age": int(rng.choice(FILER_AGES)),
                "spouse_age": int(rng.choice(FILER_AGES)),
                "head_wages": float(round(rng.uniform(0, 120_000 * income_scale))),
                "head": filer(),
                "spouse": filer() if joint else None,
                "dependents": [dependent() for _ in range(n_dependents)],
            }
        )
    # Military records come after the incomes, so drawing them does not
    # change the incomes.
    for u in units:
        u["head_military"] = _draw_military(rng)
        u["spouse_military"] = _draw_military(rng) if u["spouse"] else None
        for dependent in u["dependents"]:
            dependent["military"] = _draw_military(rng)
    return units


def _nc_coverage_units():
    # Guarantee mixed own-pay eligibility and a civilian qualifying survivor
    # without depending on a particular seed's military-record draws. Keep
    # the population budget fixed by replacing two draws in the state test.
    units = []
    for spouse_record in (MILITARY_RECORDS[1], MILITARY_RECORDS[3]):
        units.append(
            {
                "joint": True,
                "head_age": 75,
                "spouse_age": 60,
                "head_wages": 20_000.0,
                "head": {
                    **dict.fromkeys(RETIREMENT_INPUTS, 0.0),
                    "military_retirement_pay": 20_000.0,
                    "taxable_public_pension_income": 20_000.0,
                    "social_security": 20_000.0,
                },
                "spouse": {
                    **dict.fromkeys(RETIREMENT_INPUTS, 0.0),
                    "military_retirement_pay": 10_000.0,
                    "taxable_public_pension_income": 10_000.0,
                    "social_security": 0.0,
                },
                "head_military": MILITARY_RECORDS[0].copy(),
                "spouse_military": spouse_record.copy(),
                "dependents": [
                    {
                        "age": 78,
                        "income": dict.fromkeys(RETIREMENT_INPUTS, 500.0),
                        "military": MILITARY_RECORDS[0].copy(),
                    }
                ],
            }
        )
    return units


def _filers(u):
    return [u["head"]] + ([u["spouse"]] if u["spouse"] else [])


def _filer_ages(u):
    return [u["head_age"]] + ([u["spouse_age"]] if u["spouse"] else [])


def _filer_military(u):
    return [u["head_military"]] + ([u["spouse_military"]] if u["spouse"] else [])


def _nc_qualifying_military_pay(income, record):
    retiree_qualifies = (
        record["years"] >= NC_MINIMUM_SERVICE_YEARS or record["medically_retired"]
    )
    # When survivor income is recorded separately, the general military pay
    # input represents only the recipient's own retirement pay. Without a
    # separate amount, it can represent qualifying survivor benefits instead.
    own_pay_counts = retiree_qualifies or (
        record["nc_survivor"] and income["military_retirement_pay_survivors"] == 0
    )
    return (
        income["military_retirement_pay"] * own_pay_counts
        + income["military_retirement_pay_survivors"] * record["nc_survivor"]
    )


def _situation(units, states, year, *, zero_dependents=False):
    # Every group entity gets one instance per unit. Core puts every person in
    # a single instance of any group entity the situation leaves out, which
    # would pool SPM-unit benefits such as TANF across all units and states.
    people, tax_units, marital_units, households = {}, {}, {}, {}
    spm_units, families = {}, {}
    for s, state in enumerate(states):
        for i, u in enumerate(units):
            key = f"{s}_{i}"
            head = f"head_{key}"
            members = [head]
            people[head] = {
                "age": {year: u["head_age"]},
                "is_tax_unit_head": {year: True},
                "is_tax_unit_spouse": {year: False},
                "is_tax_unit_dependent": {year: False},
                "employment_income": {year: u["head_wages"]},
                **_military_inputs(u["head_military"], year),
                **{name: {year: value} for name, value in u["head"].items()},
            }
            couple = [head]
            if u["spouse"] is not None:
                spouse = f"spouse_{key}"
                members.append(spouse)
                couple.append(spouse)
                people[spouse] = {
                    "age": {year: u["spouse_age"]},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: True},
                    "is_tax_unit_dependent": {year: False},
                    **_military_inputs(u["spouse_military"], year),
                    **{name: {year: value} for name, value in u["spouse"].items()},
                }
            marital_units[f"mu_{key}"] = {"members": couple}
            factor = 0.0 if zero_dependents else 1.0
            for j, dependent in enumerate(u["dependents"]):
                child = f"child_{key}_{j}"
                members.append(child)
                marital_units[f"mu_{key}_{j}"] = {"members": [child]}
                people[child] = {
                    "age": {year: dependent["age"]},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: False},
                    "is_tax_unit_dependent": {year: True},
                    **_military_inputs(dependent["military"], year),
                    **{
                        name: {year: factor * value}
                        for name, value in dependent["income"].items()
                    },
                }
            tax_units[f"tu_{key}"] = {"members": members}
            # No unit takes up SNAP. Idaho's grocery credit is not allowed for
            # months the household receives SNAP (Idaho Code 63-3024A), so a
            # dependent's income could end the household's SNAP and raise the
            # credit: a benefit interaction, not a subtraction from the
            # filer's income, which is what these properties check.
            spm_units[f"spm_{key}"] = {
                "members": members,
                "takes_up_snap_if_eligible": {year: False},
            }
            families[f"fam_{key}"] = {"members": members}
            households[f"hh_{key}"] = {
                "members": members,
                "state_name": {year: state},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def test_tax_unit_non_dep_add_matches_reference():
    rng = np.random.default_rng(SEED)
    units = _draw_units(200, rng)
    year = 2025
    sim = Simulation(situation=_situation(units, ["TX"], year))
    tax_unit = sim.populations["tax_unit"]
    period = make_period(year)
    # Two person-level inputs and one tax-unit-level aggregate.
    variables = [
        "taxable_public_pension_income",
        "military_retirement_pay",
        "tax_unit_social_security",
    ]
    result = tax_unit_non_dep_add(tax_unit, period, variables)

    expected = []
    for u in units:
        expected.append(
            sum(
                f["taxable_public_pension_income"] + f["military_retirement_pay"]
                for f in _filers(u)
            )
        )
    expected = np.array(expected) + sim.calculate("tax_unit_social_security", year)
    np.testing.assert_allclose(result, expected, atol=TOLERANCE)

    no_dependents = np.array([not u["dependents"] for u in units])
    everyone = add(tax_unit, period, variables)
    np.testing.assert_allclose(
        result[no_dependents], everyone[no_dependents], atol=TOLERANCE
    )
    assert (result <= everyone + TOLERANCE).all()


def test_tax_unit_non_dep_add_edge_cases():
    rng = np.random.default_rng(SEED)
    units = _draw_units(20, rng)
    year = 2025
    sim = Simulation(situation=_situation(units, ["TX"], year))
    tax_unit = sim.populations["tax_unit"]
    period = make_period(year)
    # An empty list still gives one value per tax unit.
    empty = tax_unit_non_dep_add(tax_unit, period, [])
    assert empty.shape == (len(units),)
    assert (empty == 0).all()
    # A variable of another group entity falls back to add.
    np.testing.assert_allclose(
        tax_unit_non_dep_add(tax_unit, period, ["spm_unit_size"]),
        add(tax_unit, period, ["spm_unit_size"]),
    )
    with pytest.raises(ValueError):
        tax_unit_non_dep_add(sim.populations["spm_unit"], period, ["ssi"])


# States with an individual income tax on wages and retirement income.
INCOME_TAX_STATES = [
    "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "UT", "VT", "VA", "WV", "WI",
]  # fmt: skip
# These states build state income from every tax unit member's income, so a
# dependent's income can raise the filer's state AGI or taxable income (and,
# except in Iowa since 2023, the tax). That is a separate issue from
# subtracting income that never entered AGI; property 2 checks only that it
# never lowers tax there.
STATES_COUNTING_DEPENDENT_INCOME = {"AL", "AR", "IA", "MS", "NJ"}
# Intended exception per ruling d1143 (2026-10-09): follow MI-1040CR lines
# 18 and 21 (2025 MI-1040 booklet, PDF page 28 / printed page 32):
# https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=28
# Line 18 counts pensions only for the claimant and spouse; line 21 counts
# SSI received for dependent adults who live with them. A dependent adult's
# pension can reduce SSI, lower household resources and raise refundable
# credits, while the claimant's pension subtractions and tax base stay fixed.
STATES_WITH_INTENDED_RETIREMENT_TAX_DECREASES = {"MI"}
YEARS = [2025, 2026]


@pytest.mark.parametrize("year", YEARS)
def test_dependents_retirement_income_never_reduces_state_income_tax(year):
    rng = np.random.default_rng(SEED + year)
    units = _draw_units(12, rng)
    units[:2] = _nc_coverage_units()
    with_income = Simulation(situation=_situation(units, INCOME_TAX_STATES, year))
    without_income = Simulation(
        situation=_situation(units, INCOME_TAX_STATES, year, zero_dependents=True)
    )
    tax_with = with_income.calculate("state_income_tax", year)
    tax_without = without_income.calculate("state_income_tax", year)
    changed = np.zeros_like(tax_with, dtype=bool)
    for variable in ["state_agi", "state_taxable_income"]:
        changed |= (
            np.abs(
                with_income.calculate(variable, year)
                - without_income.calculate(variable, year)
            )
            > TOLERANCE
        )
    tax_changed = np.abs(tax_with - tax_without) > TOLERANCE
    states = np.repeat(INCOME_TAX_STATES, len(units))
    unit_has_dependent_income = np.array(
        [any(any(d["income"].values()) for d in u["dependents"]) for u in units]
    )
    has_dependent_income = np.tile(unit_has_dependent_income, len(INCOME_TAX_STATES))

    leaked = ~has_dependent_income & (changed | tax_changed)
    assert not leaked.any(), sorted(set(states[leaked]))

    lowered = tax_with < tax_without - TOLERANCE
    intended_exception = np.isin(
        states, list(STATES_WITH_INTENDED_RETIREMENT_TAX_DECREASES)
    )
    unexpectedly_lowered = lowered & ~intended_exception
    assert not unexpectedly_lowered.any(), sorted(set(states[unexpectedly_lowered]))

    counts_dependents = np.isin(states, list(STATES_COUNTING_DEPENDENT_INCOME))
    changed &= ~counts_dependents
    assert not changed.any(), sorted(set(states[changed]))

    # Michigan's intended exception concerns refundable credits only; a
    # dependent's pension must never enter the claimant's pension subtraction.
    mi = states == "MI"
    for variable in [
        "mi_pension_benefit",
        "mi_subtractions",
        "mi_income_tax_before_refundable_credits",
    ]:
        np.testing.assert_allclose(
            with_income.calculate(variable, year)[mi],
            without_income.calculate(variable, year)[mi],
            rtol=0,
            atol=TOLERANCE,
            err_msg=f"Michigan {variable} changed with dependent retirement income",
        )

    # The population must exercise the property, including the paths gated on
    # the filers' Social Security and on ages of 73 or more.
    assert has_dependent_income.sum() >= len(INCOME_TAX_STATES)
    filer_social_security = np.array(
        [any(f["social_security"] > 0 for f in _filers(u)) for u in units]
    )
    filer_aged_73 = np.array([max(_filer_ages(u)) >= 73 for u in units])
    elderly_dependent = np.array(
        [any(d["age"] >= 65 for d in u["dependents"]) for u in units]
    )
    assert (unit_has_dependent_income & filer_social_security).any()
    assert (unit_has_dependent_income & filer_aged_73).any()
    assert (unit_has_dependent_income & elderly_dependent).any()
    # Utah's military retirement credit is open only when the retirement
    # credit is not claimed, which needs Social Security worth more than the
    # age-gated retirement credit.
    dependent_military_pay = np.tile(
        [any(d["income"]["military_retirement_pay"] > 0 for d in u["dependents"])
         for u in units],
        len(INCOME_TAX_STATES),
    )  # fmt: skip
    ut_military_credit_open = (states == "UT") & ~with_income.calculate(
        "ut_claims_retirement_credit", year
    )
    assert (ut_military_credit_open & dependent_military_pay).any()
    # North Carolina's military deduction needs 20 years of service, a
    # medical retirement or a qualifying member's survivor benefits.
    nc = states == "NC"
    nc_military_deduction_open = nc & (
        with_income.calculate(
            "nc_military_retirement_deduction_eligible", year, map_to="tax_unit"
        )
        > 0
    )
    assert (nc_military_deduction_open & dependent_military_pay).any()

    # Property 4: each head's and spouse's own record decides whether their
    # military pay counts, whatever the other members' records.
    expected_nc_deduction = np.array(
        [
            sum(
                _nc_qualifying_military_pay(income, record)
                for income, record in zip(_filers(u), _filer_military(u))
            )
            for u in units
        ]
    )
    np.testing.assert_allclose(
        with_income.calculate("nc_military_retirement_deduction", year)[nc],
        expected_nc_deduction,
        atol=TOLERANCE,
    )
    # The draws must reach a filer whose military pay does not count next to
    # one whose pay does, and a qualifying survivor without service.
    filer_pay_counts = [
        [
            _nc_qualifying_military_pay(income, record) > 0
            for income, record in zip(_filers(u), _filer_military(u))
            if income["military_retirement_pay"] > 0
        ]
        for u in units
    ]
    assert any(any(c) and not all(c) for c in filer_pay_counts)
    assert any(
        record["nc_survivor"]
        and record["years"] == 0
        and income["military_retirement_pay"]
        + income["military_retirement_pay_survivors"]
        > 0
        for u in units
        for income, record in zip(_filers(u), _filer_military(u))
    )
