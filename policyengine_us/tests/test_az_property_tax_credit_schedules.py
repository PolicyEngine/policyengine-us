"""Arizona property tax credit Schedules 1 and 2: differential and invariant tests.

ARS 43-1072(B) gives the credit as a table of whole-dollar household income
bands: (B)(1) for a claimant who did not live with anyone ($0-1,750 -> $502,
1,751-1,850 -> $479, ..., 3,651-3,750 -> $56) and (B)(2) for one who lived with
a spouse or other persons ($0-2,500 -> $502, 2,501-2,650 -> $479, ...,
5,351-5,500 -> $56). (A)(3) limits the credit to income "less than" $3,751
and $5,501. Form 140PTC page 2 prints the same tables in 2021-2025. The
parameter files store each band's lower bound as a single_amount threshold, so
a band runs up to, but not including, the next band's lower bound, and cents
between two whole-dollar bands stay in the lower band.

Schedule 2's thresholds were once each one dollar low (2,500, 2,650, ...,
5,500), so incomes of exactly 2,500, 2,650, ..., 5,500 got the next band's
amount and 5,500 got nothing.

Differential tests compare every whole-dollar income from $0 to $7,000, and
cents near every band edge, against an independent transcription of the
statute's tables, in every year from 2021 to 2026:

- through the parameter scales, and
- through az_property_tax_credit in one vectorised simulation per schedule.

Invariants:
- Transcription: each table's bands are contiguous whole-dollar ranges from
  $0, and the last band's upper bound is one dollar below the (A)(3) limit.
- The amount never rises as income rises.
- The amount is between $56 and $502 below the (A)(3) limit and $0 at or
  above it.
- An income with cents gets the same amount as its whole dollars.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = range(2021, 2027)

# ARS 43-1072(B)(1): (lower bound, upper bound, tax credit); (A)(3)(a) limit.
SCHEDULE_1 = [
    (0, 1_750, 502),
    (1_751, 1_850, 479),
    (1_851, 1_950, 457),
    (1_951, 2_050, 435),
    (2_051, 2_150, 412),
    (2_151, 2_250, 390),
    (2_251, 2_350, 368),
    (2_351, 2_450, 345),
    (2_451, 2_550, 323),
    (2_551, 2_650, 301),
    (2_651, 2_750, 279),
    (2_751, 2_850, 256),
    (2_851, 2_950, 234),
    (2_951, 3_050, 212),
    (3_051, 3_150, 189),
    (3_151, 3_250, 167),
    (3_251, 3_350, 145),
    (3_351, 3_450, 123),
    (3_451, 3_550, 100),
    (3_551, 3_650, 78),
    (3_651, 3_750, 56),
]
SCHEDULE_1_LIMIT = 3_751

# ARS 43-1072(B)(2): (lower bound, upper bound, tax credit); (A)(3)(b) limit.
SCHEDULE_2 = [
    (0, 2_500, 502),
    (2_501, 2_650, 479),
    (2_651, 2_800, 457),
    (2_801, 2_950, 435),
    (2_951, 3_100, 412),
    (3_101, 3_250, 390),
    (3_251, 3_400, 368),
    (3_401, 3_550, 345),
    (3_551, 3_700, 323),
    (3_701, 3_850, 301),
    (3_851, 4_000, 279),
    (4_001, 4_150, 256),
    (4_151, 4_300, 234),
    (4_301, 4_450, 212),
    (4_451, 4_600, 189),
    (4_601, 4_750, 167),
    (4_751, 4_900, 145),
    (4_901, 5_050, 123),
    (5_051, 5_200, 100),
    (5_201, 5_350, 78),
    (5_351, 5_500, 56),
]
SCHEDULE_2_LIMIT = 5_501

SCHEDULES = {
    "living_alone": (SCHEDULE_1, SCHEDULE_1_LIMIT),
    "cohabitating": (SCHEDULE_2, SCHEDULE_2_LIMIT),
}

WHOLE_DOLLARS = np.arange(0, 7_001, dtype=float)
CENTS = np.array([0.01, 0.25, 0.49, 0.5, 0.51, 0.75, 0.99])


def statute_amount(table, limit, income):
    """The table amount for each income: the band holding its whole dollars."""
    dollars = np.floor(income)
    amount = np.zeros_like(income)
    for lower, upper, credit in table:
        amount = np.where((dollars >= lower) & (dollars <= upper), credit, amount)
    return np.where(income < limit, amount, 0)


def scale(name, year):
    return getattr(
        system.parameters(
            f"{year}-01-01"
        ).gov.states.az.tax.income.credits.property_tax.amount,
        name,
    )


def edge_incomes(table, limit):
    """Cents on each side of every band edge and of the (A)(3) limit."""
    edges = [lower for lower, _, _ in table[1:]] + [limit]
    return np.array(
        sorted(
            {round(e - 1 + c, 2) for e in edges for c in CENTS}
            | {round(e + c, 2) for e in edges for c in CENTS}
        )
    )


@pytest.mark.parametrize("name", SCHEDULES)
def test_transcription_is_contiguous_and_ends_below_the_limit(name):
    table, limit = SCHEDULES[name]
    assert table[0][0] == 0
    for (_, upper, _), (next_lower, _, _) in zip(table, table[1:]):
        assert next_lower == upper + 1
    assert table[-1][1] + 1 == limit


def test_both_schedules_pay_the_same_amounts():
    assert [a for *_, a in SCHEDULE_1] == [a for *_, a in SCHEDULE_2]


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("name", SCHEDULES)
def test_scale_matches_statute_at_every_whole_dollar(name, year):
    table, limit = SCHEDULES[name]
    got = scale(name, year).calc(WHOLE_DOLLARS)
    expected = statute_amount(table, limit, WHOLE_DOLLARS)
    wrong = WHOLE_DOLLARS[got != expected]
    assert wrong.size == 0, f"{name} {year}: wrong at {wrong[:10]}"


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("name", SCHEDULES)
def test_scale_matches_statute_at_cents_around_every_edge(name, year):
    table, limit = SCHEDULES[name]
    income = edge_incomes(table, limit)
    got = scale(name, year).calc(income)
    expected = statute_amount(table, limit, income)
    wrong = income[got != expected]
    assert wrong.size == 0, f"{name} {year}: wrong at {wrong[:10]}"


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("name", SCHEDULES)
def test_cents_get_the_amount_of_their_whole_dollars(name, year):
    s = scale(name, year)
    whole = s.calc(WHOLE_DOLLARS)
    for c in CENTS:
        assert (s.calc(WHOLE_DOLLARS + c) == whole).all(), (name, year, c)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("name", SCHEDULES)
def test_amount_never_rises_with_income(name, year):
    income = np.arange(0, 7_000, 0.25)
    amount = scale(name, year).calc(income)
    assert (np.diff(amount) <= 0).all()


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("name", SCHEDULES)
def test_amount_is_positive_below_the_limit_and_zero_from_it(name, year):
    _, limit = SCHEDULES[name]
    income = np.arange(0, 7_000, 0.25)
    amount = scale(name, year).calc(income)
    below = income < limit
    assert ((amount[below] >= 56) & (amount[below] <= 502)).all()
    assert (amount[~below] == 0).all()


def _credit_by_income(cohabitating, incomes, year):
    """az_property_tax_credit for one eligible tax unit per income, vectorised."""
    n = len(incomes)
    situation = {
        "people": {"head": {"age": {year: 70}}},
        "tax_units": {
            "tax_unit": {
                "members": ["head"],
                "cohabitating_spouses": {year: cohabitating},
                "az_property_tax_credit_eligible": {year: True},
            }
        },
        "households": {"household": {"members": ["head"], "state_code": {year: "AZ"}}},
        "axes": [
            [
                {
                    "name": "az_property_tax_credit_income",
                    "min": 0,
                    "max": n - 1,
                    "count": n,
                    "period": year,
                }
            ]
        ],
    }
    sim = Simulation(situation=situation)
    # Taxes paid exceed every table amount, so the credit is the table amount.
    sim.set_input("real_estate_taxes", year, np.full(n, 1_000.0))
    sim.set_input("az_property_tax_credit_income", year, np.asarray(incomes))
    return sim.calculate("az_property_tax_credit", year)


@pytest.mark.parametrize(
    "name, cohabitating", [("living_alone", False), ("cohabitating", True)]
)
def test_credit_matches_statute_in_a_vectorised_simulation(name, cohabitating):
    table, limit = SCHEDULES[name]
    year = 2025
    incomes = np.concatenate([WHOLE_DOLLARS, edge_incomes(table, limit)])
    got = _credit_by_income(cohabitating, incomes, year)
    expected = statute_amount(table, limit, incomes)
    # az_property_tax_credit_income is stored as float32; every income here
    # rounds to a float32 on the same side of each band edge.
    wrong = incomes[got != expected]
    assert wrong.size == 0, f"{name}: wrong at {wrong[:10]}"
