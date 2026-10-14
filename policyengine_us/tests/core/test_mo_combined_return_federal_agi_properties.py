"""Properties of Missouri's division of federal AGI between spouses.

Form MO-1040 Line 1 splits a couple's joint federal AGI between their two
columns with the Line 1 worksheet: each spouse's own income or loss, less
their own federal adjustments, and the columns add up to joint federal AGI
(2023 instructions, pages 6-7). 12 CSR 10-2.010(2) gives the deductible
excess of capital losses to "the spouse responsible for the excess", pro rata
when both are. From 2024 a negative amount is replaced by zero: when joint
federal AGI is zero or less both columns are zero, and when it is positive a
spouse with a negative separate amount enters zero and the other spouse the
whole joint amount (2025 instructions, page 6; 12 CSR 10-2.710(1); 12 CSR
10-2.010(5)). Line 5 subtracts each spouse's Missouri subtractions without a
floor, Line 6 adds the columns, and the Line 7 income percentage gives a
negative column 0%.

The YAML cases pin the published examples. This test checks what YAML cannot,
for every drawn couple, and for each couple both ways round: as drawn and with
the head and spouse labels exchanged. Hypothesis draws batches of Missouri
tax units (single filers and married couples filing jointly) with wages,
self-employment and rental income or losses, short- and long-term capital
gains or losses, and the spouse's own IRA, educator, early withdrawal,
alimony and health savings account deductions, U.S. obligation interest and
529 contributions. A seeded population adds breadth in one year of each
regime. Each batch is one vectorized simulation.

1. Accounting: the filers' Line 1 amounts add up to federal AGI through 2023,
   and to federal AGI floored at zero from 2024. A dependent's is zero.
2. Differential: each filer's Line 1 equals an independent numpy statement of
   the worksheet built from the inputs, with the 12 CSR 10-2.010(2)
   capital-loss rule and, from 2024, the negative-AGI rule. Line 5 equals
   Line 1 less the person's subtractions, with the MOST subtraction limited to
   what is left in 2024 and 2025 (12 CSR 10-2.010(4)(A)3 as effective
   February 29, 2024).
3. Labels: exchanging the head and spouse labels changes no person's Line 1,
   Line 5 or Missouri taxable income, and no tax unit's Missouri income tax.
4. Line 7: no one's Missouri taxable income is negative; a person whose Line
   5 is zero or less has none; the couple's taxable income is at most Line 6
   floored at zero; and when both columns are positive it is split in the
   ratio of the columns.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.05  # dollars; values are stored in float32
CAPITAL_LOSS_LIMIT = 3_000  # 26 U.S.C. 1211(b)(1), joint return

PERSON_INPUTS = [
    "employment_income",
    "self_employment_income",
    "rental_income",
    "short_term_capital_gains",
    "long_term_capital_gains",
    "traditional_ira_contributions",
    "educator_expense",
    "early_withdrawal_penalty",
    "alimony_expense",
    "health_savings_account_ald_person",
    "us_govt_interest_person",
    "investment_in_529_plan_indv",
]


def money(low, high):
    return st.integers(low, high).map(float)


def maybe(strategy):
    return st.one_of(st.just(0.0), strategy)


@st.composite
def person_amounts(draw):
    return {
        "employment_income": draw(maybe(money(1, 120_000))),
        "self_employment_income": draw(maybe(money(-60_000, 60_000))),
        "rental_income": draw(maybe(money(-20_000, 20_000))),
        "short_term_capital_gains": draw(maybe(money(-10_000, 10_000))),
        "long_term_capital_gains": draw(maybe(money(-20_000, 30_000))),
        "traditional_ira_contributions": draw(maybe(money(1, 7_000))),
        # The $300 educator expense cap applies per educator.
        "educator_expense": draw(maybe(money(1, 300))),
        "early_withdrawal_penalty": draw(maybe(money(1, 500))),
        # Alimony under a pre-2019 decree is deductible.
        "alimony_expense": draw(maybe(money(1, 15_000))),
        "health_savings_account_ald_person": draw(maybe(money(1, 4_000))),
        "us_govt_interest_person": draw(maybe(money(1, 5_000))),
        # Up to $8,000 each, so a couple stays within the $16,000 cap.
        "investment_in_529_plan_indv": draw(maybe(money(1, 8_000))),
    }


@st.composite
def tax_units(draw):
    joint = draw(st.booleans())
    return {
        "head": draw(person_amounts()),
        "spouse": draw(person_amounts()) if joint else None,
    }


SEED = 20261008


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)

    def some(low, high, p):
        return float(rng.integers(low, high + 1)) if rng.random() < p else 0.0

    def amounts():
        return {
            "employment_income": some(1, 120_000, 0.7),
            "self_employment_income": some(-60_000, 60_000, 0.4),
            "rental_income": some(-20_000, 20_000, 0.2),
            "short_term_capital_gains": some(-10_000, 10_000, 0.25),
            "long_term_capital_gains": some(-20_000, 30_000, 0.3),
            "traditional_ira_contributions": some(1, 7_000, 0.3),
            "educator_expense": some(1, 300, 0.2),
            "early_withdrawal_penalty": some(1, 500, 0.1),
            "alimony_expense": some(1, 15_000, 0.1),
            "health_savings_account_ald_person": some(1, 4_000, 0.2),
            "us_govt_interest_person": some(1, 5_000, 0.15),
            "investment_in_529_plan_indv": some(1, 8_000, 0.15),
        }

    return [
        {"head": amounts(), "spouse": amounts() if rng.random() < 0.8 else None}
        for _ in range(n)
    ]


HEAD = dict(is_tax_unit_head=True, is_tax_unit_spouse=False)
SPOUSE = dict(is_tax_unit_head=False, is_tax_unit_spouse=True)


def _person(amounts, role):
    return {
        "age": 45,
        **role,
        **amounts,
        # U.S. obligation interest is part of taxable interest.
        "taxable_interest_income": amounts["us_govt_interest_person"],
        "divorce_year": 2015,
    }


def _situation(units, year):
    """Each unit twice: as drawn, then with the labels exchanged.

    People are listed in the same order in both copies, so person k of copy
    one is the same drawn person as person k of copy two.
    """
    people = {}
    groups = {"tax_units": {}, "marital_units": {}, "households": {}}
    for copy in (0, 1):
        for i, u in enumerate(units):
            a, b = f"a_{copy}_{i}", f"b_{copy}_{i}"
            members = [a]
            if u["spouse"] is None:
                people[a] = _person(u["head"], HEAD)
            else:
                first, second = (HEAD, SPOUSE) if copy == 0 else (SPOUSE, HEAD)
                people[a] = _person(u["head"], first)
                people[b] = _person(u["spouse"], second)
                members.append(b)
            hsa = sum(people[m]["health_savings_account_ald_person"] for m in members)
            name = f"{copy}_{i}"
            groups["tax_units"][name] = {
                "members": members,
                "health_savings_account_ald": hsa,
            }
            groups["marital_units"][name] = {"members": members}
            groups["households"][name] = {"members": members, "state_code": "MO"}

    def by_year(values):
        return {k: (v if k == "members" else {year: v}) for k, v in values.items()}

    return {
        "people": {name: by_year(values) for name, values in people.items()},
        **{
            plural: {name: by_year(values) for name, values in entities.items()}
            for plural, entities in groups.items()
        },
    }


PERSON_OUTPUTS = [
    "mo_federal_adjusted_gross_income",
    "mo_adjusted_gross_income",
    "mo_taxable_income",
    "mo_agi_subtractions",
    "mo_529_deduction",
    "self_employment_tax_ald_person",
    "is_tax_unit_dependent",
]


def _run(units, year):
    sim = Simulation(situation=_situation(units, year))
    person = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON_OUTPUTS + PERSON_INPUTS
    }
    person["unit"] = sim.populations["tax_unit"].members_entity_id
    unit = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in ["adjusted_gross_income", "mo_income_tax"]
    }
    return person, unit


def _unit_sum(person, values, n):
    return np.bincount(person["unit"], weights=values, minlength=n)


def _reference_line_1(person, n, floor_applies):
    """Line 1 from the worksheet: each spouse's own income or loss less their
    own adjustments, with 12 CSR 10-2.010(2) for a net capital loss."""
    own = (
        person["employment_income"]
        + person["self_employment_income"]
        + person["rental_income"]
        + person["us_govt_interest_person"]
        - person["self_employment_tax_ald_person"]
        - person["traditional_ira_contributions"]
        - person["educator_expense"]
        - person["early_withdrawal_penalty"]
        - person["alimony_expense"]
        - person["health_savings_account_ald_person"]
    )
    short = person["short_term_capital_gains"]
    long = person["long_term_capital_gains"]
    net = _unit_sum(person, short + long, n)[person["unit"]]
    # Each character's net loss, attributed to the spouses with losses of
    # that character (Example No. 2).
    responsibility = 0.0
    for amount in (short, long):
        character_net = _unit_sum(person, amount, n)[person["unit"]]
        own_loss = np.maximum(0, -amount)
        unit_loss = _unit_sum(person, own_loss, n)[person["unit"]]
        share = np.divide(
            own_loss, unit_loss, out=np.zeros_like(own_loss), where=unit_loss > 0
        )
        responsibility = responsibility + np.maximum(0, -character_net) * share
    unit_responsibility = _unit_sum(person, responsibility, n)[person["unit"]]
    loss_share = np.divide(
        responsibility,
        unit_responsibility,
        out=np.zeros_like(responsibility),
        where=unit_responsibility > 0,
    )
    deductible_loss = np.minimum(CAPITAL_LOSS_LIMIT, np.maximum(0, -net))
    # With a net gain each spouse's own gain or loss is in their column; with
    # a net loss the gains drop out and each takes their share of the
    # deductible loss.
    capital = np.where(net >= 0, short + long, -deductible_loss * loss_share)
    separate = own + capital
    if not floor_applies:
        return separate
    joint = _unit_sum(person, separate, n)[person["unit"]]
    has_negative = _unit_sum(person, (separate < 0).astype(float), n)[person["unit"]]
    line_1 = np.where(separate < 0, 0, np.where(has_negative > 0, joint, separate))
    return np.where(joint > 0, line_1, 0)


def _check(units, year):
    person, unit = _run(units, year)
    n = len(unit["adjusted_gross_income"])
    line_1 = person["mo_federal_adjusted_gross_income"]
    line_5 = person["mo_adjusted_gross_income"]
    taxable = person["mo_taxable_income"]
    # The years come from the sources, not from the model's parameters:
    # 12 CSR 10-2.710(1) and the 2024 and 2025 instructions from 2024, and
    # the MOST limit under the 12 CSR 10-2.010 version effective February 29,
    # 2024 for 2024 and 2025.
    floor_applies = year >= 2024
    most_limited = 2024 <= year <= 2025

    # 1. Accounting.
    agi = unit["adjusted_gross_income"]
    expected_total = np.maximum(0, agi) if floor_applies else agi
    np.testing.assert_allclose(
        _unit_sum(person, line_1, n), expected_total, atol=TOLERANCE
    )
    assert (line_1[person["is_tax_unit_dependent"] > 0] == 0).all()

    # 2. Differential against the worksheet.
    np.testing.assert_allclose(
        line_1, _reference_line_1(person, n, floor_applies), atol=TOLERANCE
    )
    most = person["mo_529_deduction"]
    other = person["mo_agi_subtractions"] - most
    if most_limited:
        most = np.minimum(most, np.maximum(0, line_1 - other))
    np.testing.assert_allclose(line_5, line_1 - other - most, atol=TOLERANCE)

    # 3. Labels: the second half of the people and tax units is the first
    # half with the labels exchanged.
    half_people, half_units = len(line_1) // 2, n // 2
    for values in (line_1, line_5, taxable):
        np.testing.assert_allclose(
            values[:half_people], values[half_people:], atol=TOLERANCE
        )
    tax = unit["mo_income_tax"]
    np.testing.assert_allclose(tax[:half_units], tax[half_units:], atol=TOLERANCE)

    # 4. Line 7.
    assert (taxable >= -TOLERANCE).all()
    assert (np.abs(taxable[line_5 <= 0]) <= TOLERANCE).all()
    line_6 = _unit_sum(person, line_5, n)
    assert (_unit_sum(person, taxable, n) <= np.maximum(0, line_6) + TOLERANCE).all()
    other_line_5 = _unit_sum(person, line_5, n)[person["unit"]] - line_5
    other_taxable = _unit_sum(person, taxable, n)[person["unit"]] - taxable
    both_positive = (line_5 > 0) & (other_line_5 > 0)
    np.testing.assert_allclose(
        (taxable * other_line_5)[both_positive],
        (other_taxable * line_5)[both_positive],
        rtol=1e-4,
        atol=1.0,
    )


# Each example is one vectorized batch of tax units, so a few examples cover
# many units; the seeded population runs once per year.
SETTINGS = dict(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(
    st.lists(tax_units(), min_size=10, max_size=40),
    st.sampled_from([2022, 2024, 2025, 2026]),
)
def test_mo_federal_agi_division_properties(units, year):
    _check(units, year)


# One year in each regime: columns may be negative (2023); the negative-AGI
# rule with the MOST limit (2025); the negative-AGI rule without it (2026).
@pytest.mark.parametrize("year", [2023, 2025, 2026])
def test_seeded_population(year):
    _check(_seeded_units(), year)
