"""State income taxes do not depend on which spouse is labelled head.

Which spouse a married couple lists first on a return is a convention of the
form. States tax "the taxpayer and spouse" alike, and spouses who file
separately on one return each report their own income in their own column
(Arkansas Filing Status 4, Delaware Filing Status 4, Iowa status 3,
Mississippi's combined return, Montana Filing Status 2a). So exchanging the
two adults' `is_tax_unit_head` and `is_tax_unit_spouse` labels, with every
other input kept, must leave each state's income tax unchanged.

On main these depended on the label:
- Arkansas, Delaware, Iowa, Mississippi and Montana put the dependents' income
  the model counts on the head's column before taxing each column separately.
  It now goes on the column of the spouse with the greater income of their
  own, and an exact tie splits it (move_dependent_amounts_to_filer).
- Delaware's combined separate return routed the EITC and the dependent care
  credit by label on equal incomes and split the dependent personal credits
  with a heuristic. They are now chosen together to minimise tax.
- Montana's joint itemized deductions counted only the head's mortgage and
  investment interest.
- Minnesota's child and dependent care credit and Montana's dependent care
  deduction accepted an incapacitated spouse but not an incapacitated head.
- Missouri's property tax credit tested the survivor pathway, and Oklahoma's
  the disability pathway, on the head only.
- Oregon's working family household and dependent care credit excluded a
  disabled head as a qualifying spouse and counted only the head's earnings.
- Mississippi's health savings account and self-employed adjustments put a
  tax-unit deduction with no per-person split on the head's column.

Couples where a spouse is claimed as a dependent on another return are out
of scope here: the federal standard deduction and several state formulas
read only `head_is_dependent_elsewhere`, so this test leaves that input at
its default.

Hypothesis draws batches of married couples, with and without dependents
(who may have income), in the nine states above for 2021-2026. A seeded
population of those states, with crafted edge cases (offsetting incomes,
spouses with equal income, one disabled, incapacitated, elderly or surviving
spouse, interest paid by one spouse), adds breadth in every year, and three
seeded couples in every state guard current law (2026) everywhere else. Each
batch runs as one vectorized simulation that holds every couple twice, as
drawn and with the head and spouse labels exchanged. For each couple:

1. Swap invariance: state income tax, before and after refundable credits,
   is finite and the same to the cent.
2. The per-person columns (`ar_agi_indiv`, `de_agi_indiv`, `ia_net_income`,
   `ms_agi`, `mt_agi_indiv`) are the same for each person, to the cent.
3. Differential: in Arkansas, Delaware, Iowa and Mississippi those columns
   equal an independent numpy allocation of each person's own amount, which
   conserves the tax unit's total. Montana's own amounts are not
   reconstructed, so it is checked by 1 and 2 only.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.model_api import STATES

TOLERANCE = 0.01  # dollars: the same to the cent
# The differential compares float32 model values with float64 numpy sums of
# them, so it also allows float32 rounding.
FLOAT32_RTOL = 1e-6
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
AFFECTED = ["AR", "DE", "IA", "MN", "MO", "MS", "MT", "OK", "OR"]
ALL_STATES = [s for s in STATES if s not in ("PR", "VI")]
TAX_UNIT_OUTPUTS = [
    "state_income_tax",
    "state_income_tax_before_refundable_credits",
]
COLUMNS = ["ar_agi_indiv", "de_agi_indiv", "ia_net_income", "ms_agi", "mt_agi_indiv"]


def money(high):
    return st.one_of(st.just(0.0), st.integers(1, high).map(float))


def gain_or_loss(low, high):
    return st.one_of(st.just(0.0), st.integers(low, high).map(float))


@st.composite
def adults(draw):
    return {
        "age": draw(st.integers(18, 90)),
        "is_blind": draw(st.booleans()),
        "is_disabled": draw(st.booleans()),
        "employment_income": draw(money(150_000)),
        "self_employment_income": draw(gain_or_loss(-20_000, 80_000)),
        "taxable_interest_income": draw(money(10_000)),
        "qualified_dividend_income": draw(money(10_000)),
        "long_term_capital_gains": draw(gain_or_loss(-5_000, 50_000)),
        "rental_income": draw(gain_or_loss(-10_000, 30_000)),
        "social_security_retirement": draw(money(40_000)),
        "taxable_private_pension_income": draw(money(50_000)),
        "taxable_ira_distributions": draw(money(30_000)),
        "military_retirement_pay": draw(money(30_000)),
        "unemployment_compensation": draw(money(12_000)),
        "traditional_ira_contributions": draw(money(7_000)),
        "student_loan_interest": draw(money(2_500)),
        "real_estate_taxes": draw(money(12_000)),
        "deductible_mortgage_interest": draw(money(20_000)),
        "investment_interest_expense": draw(money(5_000)),
        "charitable_cash_donations": draw(money(8_000)),
        "other_medical_expenses": draw(money(15_000)),
        "is_incapable_of_self_care": draw(st.booleans()),
        "pre_subsidy_care_expenses": draw(money(6_000)),
        "social_security_survivors": draw(money(20_000)),
        "is_fully_disabled_service_connected_veteran": draw(st.booleans()),
    }


@st.composite
def dependents(draw):
    age = draw(st.integers(0, 23))
    return {
        "age": age,
        "is_full_time_student": age >= 18,
        "employment_income": draw(money(25_000)),
        "self_employment_income": draw(gain_or_loss(-3_000, 8_000)),
        "taxable_interest_income": draw(money(3_000)),
        "qualified_dividend_income": draw(money(3_000)),
        "long_term_capital_gains": draw(gain_or_loss(-2_000, 5_000)),
        "pre_subsidy_childcare_expenses": draw(money(10_000)),
        # The model counts these on the filers' return in Delaware and
        # Montana; no formula computes them.
        "de_additions": draw(money(3_000)),
        "mt_additions": draw(money(3_000)),
    }


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(AFFECTED)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=3)),
        # Tax-unit deductions with no per-person split, as microdata supply
        # the health savings account deduction.
        "tax_unit": {
            "health_savings_account_ald": draw(money(8_550)),
            "self_employed_health_insurance_ald": draw(money(6_000)),
        },
    }


SEED = 20261007


def _seeded_adult(rng):
    def some(high, p):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    def signed(low, high, p):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    age = int(rng.integers(18, 91))
    return {
        "age": age,
        "is_blind": bool(rng.random() < 0.1),
        "is_disabled": bool(rng.random() < 0.1),
        "employment_income": some(150_000, 0.7),
        "self_employment_income": signed(-20_000, 80_000, 0.25),
        "taxable_interest_income": some(10_000, 0.4),
        "qualified_dividend_income": some(10_000, 0.25),
        "long_term_capital_gains": signed(-5_000, 50_000, 0.2),
        "rental_income": signed(-10_000, 30_000, 0.12),
        "social_security_retirement": some(40_000, 0.5 if age >= 62 else 0.03),
        "taxable_private_pension_income": some(50_000, 0.45 if age >= 55 else 0.05),
        "taxable_ira_distributions": some(30_000, 0.2 if age >= 59 else 0.03),
        "military_retirement_pay": some(30_000, 0.04),
        "unemployment_compensation": some(12_000, 0.06),
        "traditional_ira_contributions": some(7_000, 0.15),
        "student_loan_interest": some(2_500, 0.1),
        "real_estate_taxes": some(12_000, 0.35),
        "deductible_mortgage_interest": some(20_000, 0.25),
        "investment_interest_expense": some(5_000, 0.08),
        "charitable_cash_donations": some(8_000, 0.3),
        "other_medical_expenses": some(15_000, 0.2),
        "is_incapable_of_self_care": bool(rng.random() < 0.05),
        "pre_subsidy_care_expenses": some(6_000, 0.05),
        "social_security_survivors": some(20_000, 0.05 if age >= 55 else 0.0),
        "is_fully_disabled_service_connected_veteran": bool(rng.random() < 0.03),
    }


def _seeded_dependent(rng):
    def some(high, p):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    age = int(rng.integers(0, 24))
    return {
        "age": age,
        "is_full_time_student": age >= 18,
        "employment_income": some(25_000, 0.5 if age >= 14 else 0.0),
        "self_employment_income": some(8_000, 0.1 if age >= 14 else 0.0),
        "taxable_interest_income": some(3_000, 0.3),
        "qualified_dividend_income": some(3_000, 0.15),
        "long_term_capital_gains": some(5_000, 0.08),
        "pre_subsidy_childcare_expenses": some(10_000, 0.5 if age < 13 else 0.0),
        "de_additions": some(3_000, 0.1),
        "mt_additions": some(3_000, 0.1),
    }


def _review_cases():
    # The cases in the review of PolicyEngine/policyengine-us#9617: adults
    # with $60,000 and $10,000 in Arkansas and $100,000 and $30,000 in
    # Delaware, each with a dependent earning $20,000.
    def adult(wages):
        return {"age": 45, "employment_income": wages}

    dependent = {"age": 17, "employment_income": 20_000.0}
    return [
        {
            "state": "AR",
            "adults": [adult(60_000.0), adult(10_000.0)],
            "dependents": [dependent],
        },
        {
            "state": "DE",
            "adults": [adult(100_000.0), adult(30_000.0)],
            "dependents": [dependent],
        },
    ]


def _edge_cases(states):
    # Couples that random draws rarely produce, in each of the states.
    def adult(age=45, **amounts):
        return {"age": age, **amounts}

    teen = {"age": 17, "employment_income": 9_000.0, "taxable_interest_income": 900.0}
    itemized = {
        "real_estate_taxes": 9_000.0,
        "deductible_mortgage_interest": 30_000.0,
        "charitable_cash_donations": 4_000.0,
    }
    couples = [
        # Offsetting self-employment income, so the couple's total is zero.
        (
            [
                adult(self_employment_income=30_000.0, **itemized),
                adult(self_employment_income=-30_000.0),
            ],
            [teen],
        ),
        # Spouses with equal income and a dependent with income.
        (
            [adult(employment_income=45_000.0), adult(employment_income=45_000.0)],
            [teen],
        ),
        ([adult(), adult()], [teen]),
        # One spouse has all the income; the dependent too.
        (
            [adult(employment_income=90_000.0), adult()],
            [teen, {"age": 15, "taxable_interest_income": 2_000.0}],
        ),
        # Interest paid by one spouse, enough to itemize.
        (
            [
                adult(employment_income=120_000.0),
                adult(
                    employment_income=30_000.0,
                    **itemized,
                    investment_interest_expense=6_000.0,
                    taxable_interest_income=9_000.0,
                ),
            ],
            [],
        ),
        # Low income, property tax, one totally disabled spouse under 65.
        (
            [
                adult(40, employment_income=6_000.0, real_estate_taxes=900.0),
                adult(40, is_disabled=True),
            ],
            [],
        ),
        # One spouse 65 or older, the other young, low income.
        (
            [
                adult(
                    70, social_security_retirement=14_000.0, real_estate_taxes=2_500.0
                ),
                adult(50, employment_income=8_000.0),
            ],
            [],
        ),
        # One blind spouse.
        (
            [
                adult(80, social_security_retirement=20_000.0, is_blind=True),
                adult(30, employment_income=25_000.0),
            ],
            [],
        ),
        # One incapacitated spouse with care expenses; the other earns and
        # pays property tax (review of #9981).
        (
            [
                adult(employment_income=20_000.0, real_estate_taxes=12_000.0),
                adult(
                    is_incapable_of_self_care=True, pre_subsidy_care_expenses=4_000.0
                ),
            ],
            [],
        ),
        # Equal incomes, different ages and a child without income: credit
        # routing on ties (review of #9981).
        (
            [
                adult(60, employment_income=20_000.0),
                adult(45, employment_income=20_000.0),
            ],
            [{"age": 10}],
        ),
        # A surviving spouse aged 60 with a low-income spouse who pays
        # property tax (review of #9981).
        (
            [
                adult(60, employment_income=6_000.0, real_estate_taxes=900.0),
                adult(60, social_security_survivors=6_000.0),
            ],
            [],
        ),
        # One disabled spouse who cannot care for themselves, with care
        # expenses; the other earns (review round 2 of #9981).
        (
            [
                adult(employment_income=20_000.0),
                adult(
                    is_disabled=True,
                    is_incapable_of_self_care=True,
                    pre_subsidy_care_expenses=4_000.0,
                ),
            ],
            [],
        ),
        # One spouse a 100% disabled veteran, low income, rent.
        (
            [
                adult(55, employment_income=8_000.0, rent=7_200.0),
                adult(55, is_fully_disabled_service_connected_veteran=True),
            ],
            [],
        ),
    ]
    edge = [
        {"state": state, "adults": adults, "dependents": deps}
        for state in states
        for adults, deps in couples
    ]
    # A tax-unit health savings account deduction with no per-person split
    # and unequal incomes, as in the microdata (#9617 cross-check).
    edge += [
        {
            "state": state,
            "adults": [
                adult(employment_income=300_000.0),
                adult(employment_income=2_000.0),
            ],
            "dependents": [teen],
            "tax_unit": {"health_savings_account_ald": 9_000.0},
        }
        for state in states
    ]
    return edge


def _seeded_couples(states, per_state):
    rng = np.random.default_rng(SEED)
    return [
        {
            "state": state,
            "adults": [_seeded_adult(rng), _seeded_adult(rng)],
            # Most couples have dependents.
            "dependents": [
                _seeded_dependent(rng) for _ in range(int(rng.choice([0, 1, 1, 2, 3])))
            ],
            "tax_unit": {
                "health_savings_account_ald": (
                    float(round(rng.uniform(1, 8_550))) if rng.random() < 0.3 else 0.0
                ),
            },
        }
        for state in states
        for _ in range(per_state)
    ]


def _situation(units, year):
    people = {}
    groups = {
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for i, unit in enumerate(units):
        # The second copy exchanges the head and spouse labels; people keep
        # their order and every other input.
        for copy in (0, 1):
            a, b = f"a_{i}_{copy}", f"b_{i}_{copy}"
            for name, amounts, is_head in (
                (a, unit["adults"][0], copy == 0),
                (b, unit["adults"][1], copy == 1),
            ):
                people[name] = {
                    **amounts,
                    "is_tax_unit_head": is_head,
                    "is_tax_unit_spouse": not is_head,
                    "is_tax_unit_dependent": False,
                }
            members = [a, b]
            groups["marital_units"][f"couple_{i}_{copy}"] = {"members": [a, b]}
            for j, amounts in enumerate(unit["dependents"]):
                child = f"dependent_{i}_{copy}_{j}"
                people[child] = {
                    **amounts,
                    "is_tax_unit_head": False,
                    "is_tax_unit_spouse": False,
                    "is_tax_unit_dependent": True,
                }
                members.append(child)
                groups["marital_units"][f"single_{i}_{copy}_{j}"] = {"members": [child]}
            for group, prefix in (
                ("tax_units", "tax_unit"),
                ("spm_units", "spm_unit"),
                ("families", "family"),
            ):
                groups[group][f"{prefix}_{i}_{copy}"] = {"members": members}
            groups["tax_units"][f"tax_unit_{i}_{copy}"].update(
                {k: {year: v} for k, v in unit.get("tax_unit", {}).items()}
            )
            groups["households"][f"household_{i}_{copy}"] = {
                "members": members,
                "state_code": {year: unit["state"]},
            }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _own_amounts(sim, year, column):
    # Each person's own amount before dependents' amounts are moved, from the
    # column's inputs.
    def calc(name):
        return np.asarray(sim.calculate(name, year), dtype=float)

    if column == "ar_agi_indiv":
        return np.maximum(calc("ar_gross_income_indiv") - calc("ar_exemptions"), 0)
    if column == "de_agi_indiv":
        return np.maximum(
            calc("de_pre_exclusions_agi")
            - calc("de_elderly_or_disabled_income_exclusion_indiv"),
            0,
        )
    if column == "ia_net_income":
        return calc("ia_gross_income") - calc("ia_income_adjustments")
    if column == "ms_agi":
        p = sim.tax_benefit_system.parameters(year).gov.states.ms.tax.income
        net = sum(calc(source) for source in p.income_sources) - calc(
            "ms_agi_adjustments"
        )
        dependent = calc("is_tax_unit_dependent").astype(bool)
        return np.where(dependent, np.maximum(net, 0), net)
    raise ValueError(column)


def _reference_allocation(own, unit, head, spouse, dependent):
    # Independent numpy statement of the rule: the spouse whose own amount is
    # greater takes the dependents' total; an exact tie splits it equally.
    n_units = unit.max() + 1

    def unit_sum(mask):
        return np.bincount(unit, weights=own * mask, minlength=n_units)

    head_own = unit_sum(head)[unit]
    spouse_own = unit_sum(spouse)[unit]
    dependents_total = unit_sum(dependent)[unit]
    has_spouse = np.bincount(unit, weights=spouse, minlength=n_units)[unit] > 0
    mine = np.where(head, head_own, spouse_own)
    other = np.where(head, spouse_own, head_own)
    share = np.where(mine > other, 1.0, np.where(mine == other, 0.5, 0.0))
    share = np.where(has_spouse, share, 1.0) * (head | spouse)
    return np.where(dependent, 0.0, own) + share * dependents_total


def _check(units, year):
    sim = Simulation(situation=_situation(units, year))
    states = np.array([u["state"] for u in units])

    # 1. Swap invariance of each state's income tax.
    for name in TAX_UNIT_OUTPUTS:
        values = np.asarray(sim.calculate(name, year), dtype=float)
        assert np.isfinite(values).all(), f"{name} in {year} is not finite"
        drawn, swapped = values[0::2], values[1::2]
        differs = ~(np.abs(swapped - drawn) <= TOLERANCE)
        assert not differs.any(), (
            f"{name} in {year} changes when the head and spouse labels are "
            f"exchanged: "
            + ", ".join(
                f"{states[i]} {drawn[i]:.2f} -> {swapped[i]:.2f}"
                for i in np.flatnonzero(differs)[:10]
            )
        )

    # Tax units are numbered in the order _situation adds them: couple i's
    # first copy is unit 2i and its second copy is unit 2i + 1.
    unit = np.asarray(sim.populations["tax_unit"].members_entity_id)
    head = np.asarray(sim.calculate("is_tax_unit_head", year), dtype=bool)
    spouse = np.asarray(sim.calculate("is_tax_unit_spouse", year), dtype=bool)
    dependent = np.asarray(sim.calculate("is_tax_unit_dependent", year), dtype=bool)
    # People keep their order in both copies, so person k of a couple's first
    # copy is person k of its second.
    first_copy = unit % 2 == 0
    for column in COLUMNS:
        values = np.asarray(sim.calculate(column, year), dtype=float)
        assert np.isfinite(values).all(), f"{column} in {year} is not finite"
        # 2. Each person's column is the same under either labelling.
        np.testing.assert_allclose(
            values[~first_copy],
            values[first_copy],
            rtol=0,
            atol=TOLERANCE,
            equal_nan=False,
            err_msg=f"{column} in {year}",
        )
        if column == "mt_agi_indiv":
            continue
        # 3. Differential against the numpy allocation, where the column
        # applies (its state, and its years for Iowa).
        own = _own_amounts(sim, year, column)
        reference = _reference_allocation(own, unit, head, spouse, dependent)
        in_state = states[unit // 2] == column[:2].upper()
        np.testing.assert_allclose(
            values[in_state],
            reference[in_state],
            rtol=FLOAT32_RTOL,
            atol=TOLERANCE,
            equal_nan=False,
            err_msg=f"{column} in {year}",
        )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
@settings(
    max_examples=12,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=10, max_size=40))
def test_state_income_tax_does_not_depend_on_head_label(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    units = _seeded_couples(AFFECTED, per_state=20)
    _check(units + _edge_cases(AFFECTED) + _review_cases(), year)


def test_every_state_under_current_law():
    # Simulating every state's earlier years makes this the costliest batch,
    # so the guard outside the nine states runs for one year.
    _check(_seeded_couples(ALL_STATES, per_state=3), 2026)
