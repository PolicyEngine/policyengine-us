"""Invariants of Minnesota's property tax and charitable deductions.

The Minnesota Legislature caps the deduction for real estate and personal
property taxes at $10,000 for both together, or $5,000 for a married person
filing separately, from tax year 2019 (Minn. Stat. 290.0122, subd. 3(a)(1)).
From tax year 2026 it allows charitable contributions over 1% of the
contribution base (subd. 4(a)), where Congress allows those over 0.5% (26
U.S.C. 170(b)(1)(I)). It gives a non-itemizer half of the allowable
contributions over $500 (section 290.0132, subd. 7), and it keeps the federal
section 170 deduction in alternative minimum taxable income (section 290.091,
subd. 2(a)(2)(i)).

The YAML files for these variables pin the amounts at each threshold. The
checks below take their caps, floors and years from those statutes, and hold
for every tax unit in a grid of filing statuses, incomes, taxes and gifts.
Each year's units share one simulation.

Property taxes, in 2019, 2024 and 2026:

1. The deduction lies between 0 and the lesser of the taxes paid and the cap.
2. Swapping the real estate and personal property amounts leaves it unchanged.
3. Paying more of either tax never lowers it.
4. Itemized deductions rise by the deduction.

Charitable contributions, in 2025 and 2026:

5. The Minnesota amount lies between 0 and the amount before any floor, and
   giving more never lowers it.
6. Before 2026, it equals the federal deduction. From 2026, a filer deducts
   gifts in Minnesota only when they exceed 1% of income, and the Minnesota
   amount trails the federal one by at most 0.5% of income.
7. The federal deduction equals the amount before any floor, less 0.5% of
   income from 2026. The grid includes gifts over the percentage ceilings,
   where the two variables would differ if only one of them applied a
   ceiling.
8. Itemized deductions rise by the Minnesota amount, and an itemizer's
   alternative minimum taxable income falls by the federal amount.
9. An itemizer takes no charity subtraction. A non-itemizer takes one only
   when the Minnesota amount exceeds $500.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

STATUSES = (
    "SINGLE",
    "SEPARATE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)

# Minn. Stat. 290.0122, subd. 3(a)(1).
PROPERTY_TAX_CAP = 10_000
PROPERTY_TAX_CAP_SEPARATE = 5_000
PROPERTY_YEARS = (2019, 2024, 2026)
TAXES = (0, 3_000, 7_000, 18_000)
PROPERTY_UNITS = list(product(STATUSES, TAXES, TAXES))
# Below every reduction threshold in subd. 2, so itemized deductions equal
# the sum of their parts.
PROPERTY_AGI = 50_000

# Minn. Stat. 290.0122, subd. 4(a), and 26 U.S.C. 170(b)(1)(I), both for
# taxable years beginning after December 31, 2025.
FLOOR_YEAR = 2026
MINNESOTA_FLOOR = 0.01
FEDERAL_FLOOR = 0.005
# Minn. Stat. 290.0132, subd. 7.
SUBTRACTION_THRESHOLD = 500
CHARITY_YEARS = (2025, 2026)
# Both incomes lie below every reduction threshold in subd. 2.
AGIS = (50_000, 100_000)
# With 40,000 of mortgage interest every unit itemizes.
MORTGAGE_INTEREST = (0, 40_000)
# (cash, other property). Gifts of 400 and 600 fall on either side of 1% of
# 50,000, and 600 falls between the two floors at 100,000. Gifts of 80,000
# exceed the 60% and 50% ceilings at both incomes.
GIFTS = (
    (0, 0),
    (400, 0),
    (600, 0),
    (1_500, 0),
    (80_000, 0),
    (0, 80_000),
    (20_000, 20_000),
)
CHARITY_UNITS = list(product(STATUSES, AGIS, MORTGAGE_INTEREST, GIFTS))


def _simulation(year, units):
    """One Minnesota tax unit per (filing status, income, person inputs)."""
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i, (status, agi, inputs) in enumerate(units):
        person = f"p{i}"
        people[person] = {
            "age": {period: 40},
            **{name: {period: amount} for name, amount in inputs.items()},
        }
        tax_units[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: status},
            "adjusted_gross_income": {period: agi},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: "MN"}}
    return Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )


@pytest.mark.parametrize("year", PROPERTY_YEARS)
def test_property_tax_deduction_invariants(year):
    period = str(year)
    simulation = _simulation(
        year,
        [
            (
                status,
                PROPERTY_AGI,
                {"real_estate_taxes": real, "mn_personal_property_taxes": personal},
            )
            for status, real, personal in PROPERTY_UNITS
        ],
    )
    deduction = simulation.calculate("mn_property_tax_deduction", period)
    itemized = simulation.calculate("mn_itemized_deductions", period)
    index = {unit: i for i, unit in enumerate(PROPERTY_UNITS)}

    for (status, real, personal), i in index.items():
        label = f"{year} {status} real {real} personal {personal}"
        cap = PROPERTY_TAX_CAP_SEPARATE if status == "SEPARATE" else PROPERTY_TAX_CAP

        # 1. Between 0 and the lesser of the taxes paid and the cap.
        assert deduction[i] >= 0, label
        assert deduction[i] <= min(real + personal, cap) + TOLERANCE, label

        # 2. Swapping the two taxes leaves the deduction unchanged.
        swapped = index[status, personal, real]
        assert deduction[i] == pytest.approx(deduction[swapped], abs=TOLERANCE), label

        # 3. Paying more of either tax never lowers it.
        for more_real, more_personal in product(TAXES, TAXES):
            if more_real >= real and more_personal >= personal:
                more = index[status, more_real, more_personal]
                assert deduction[more] >= deduction[i] - TOLERANCE, label

        # 4. Itemized deductions rise by the deduction.
        no_taxes = index[status, 0, 0]
        assert itemized[i] - itemized[no_taxes] == pytest.approx(
            deduction[i], abs=TOLERANCE
        ), label

    # The grid has filers who pay no tax and filers at the cap.
    assert deduction.min() == 0
    assert deduction.max() == pytest.approx(PROPERTY_TAX_CAP, abs=TOLERANCE)


@pytest.mark.parametrize("year", CHARITY_YEARS)
def test_charitable_deduction_invariants(year):
    period = str(year)
    simulation = _simulation(
        year,
        [
            (
                status,
                agi,
                {
                    "deductible_mortgage_interest": mortgage,
                    "charitable_cash_donations": cash,
                    "charitable_non_cash_donations": other,
                },
            )
            for status, agi, mortgage, (cash, other) in CHARITY_UNITS
        ],
    )
    before_floor = simulation.calculate("charitable_deduction_before_floor", period)
    federal = simulation.calculate("charitable_deduction", period)
    minnesota = simulation.calculate("mn_charitable_deduction", period)
    itemized = simulation.calculate("mn_itemized_deductions", period)
    itemizing = simulation.calculate("mn_itemizing", period)
    subtraction = simulation.calculate("mn_charity_subtraction", period)
    amt_income = simulation.calculate("mn_amt_taxable_income", period)
    index = {unit: i for i, unit in enumerate(CHARITY_UNITS)}

    for (status, agi, mortgage, (cash, other)), i in index.items():
        label = f"{year} {status} AGI {agi} mortgage {mortgage} gifts {(cash, other)}"

        # 5. Between 0 and the amount before any floor; more gifts never
        # lower it.
        assert minnesota[i] >= 0, label
        assert minnesota[i] <= before_floor[i] + TOLERANCE, label
        for more_cash, more_other in GIFTS:
            if more_cash >= cash and more_other >= other:
                more = index[status, agi, mortgage, (more_cash, more_other)]
                assert minnesota[more] >= minnesota[i] - TOLERANCE, label

        if year < FLOOR_YEAR:
            # 6. Minnesota follows the federal deduction.
            assert minnesota[i] == pytest.approx(federal[i], abs=TOLERANCE), label
            # 7. No floor applies.
            assert federal[i] == pytest.approx(before_floor[i], abs=TOLERANCE), label
        else:
            # 6. A deduction only for gifts over 1% of income, at most 0.5%
            # of income below the federal one.
            over_floor = before_floor[i] > MINNESOTA_FLOOR * agi + TOLERANCE
            assert (minnesota[i] > TOLERANCE) == over_floor, label
            gap = federal[i] - minnesota[i]
            assert gap >= -TOLERANCE, label
            assert gap <= (MINNESOTA_FLOOR - FEDERAL_FLOOR) * agi + TOLERANCE, label
            # 7. The federal floor applies to the same amount.
            assert federal[i] == pytest.approx(
                max(0, before_floor[i] - FEDERAL_FLOOR * agi), abs=TOLERANCE
            ), label

        # 8. Itemized deductions rise by the Minnesota amount. An itemizer's
        # AMT income falls by the federal amount.
        no_gifts = index[status, agi, mortgage, (0, 0)]
        assert itemized[i] - itemized[no_gifts] == pytest.approx(
            minnesota[i], abs=TOLERANCE
        ), label
        if itemizing[i] and itemizing[no_gifts]:
            assert amt_income[no_gifts] - amt_income[i] == pytest.approx(
                federal[i], abs=TOLERANCE
            ), label

        # 9. No subtraction for an itemizer; one for a non-itemizer only
        # when the Minnesota amount exceeds $500.
        if itemizing[i]:
            assert subtraction[i] == 0, label
        else:
            over_threshold = minnesota[i] > SUBTRACTION_THRESHOLD + TOLERANCE
            assert (subtraction[i] > TOLERANCE) == over_threshold, label

    # The grid has itemizers and non-itemizers, a subtraction, gifts over
    # and under the percentage ceilings and, from 2026, gifts between the
    # two floors.
    gifts = np.array([cash + other for *_, (cash, other) in CHARITY_UNITS])
    assert itemizing.any() and not itemizing.all()
    assert (subtraction > 0).any()
    assert (before_floor < gifts - TOLERANCE).any()
    assert ((before_floor > 0) & (before_floor > gifts - TOLERANCE)).any()
    if year >= FLOOR_YEAR:
        assert ((federal > 0) & (minnesota == 0)).any()
        assert (minnesota > 0).any()
