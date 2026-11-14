"""Property tests: Vermont's 2017 taxable income under former 32 V.S.A.
§ 5811(21).

For 2017, Vermont taxable income is federal taxable income, before its zero
floor, plus the itemized deduction addback and other additions, less the
subtractions, floored at zero. Schedule IN-155 computes the addback. For
allowed federal itemized deductions I (Schedule A line 29, after section 68
and including wagering losses), deducted income taxes T, medical M,
charitable C and federal standard deduction S, it is min(rT, max(I - S, 0))
+ max(I - rT - M - rC - 2.5 S, 0) for an itemizer and zero otherwise. r is
the Department's worksheet ratio: the share of the deductions section 68
limits that remains after the limitation (1 when none are limited).

Properties checked, each in one batched simulation per example:

1. max(I - SALT - M - C - 2.5 S, 0) <= addback <= max(I - S, 0) +
   max(I - 2.5 S, 0) for an itemizer, and the addback is zero for a
   nonitemizer.
2. The addback never falls when I rises with T, M, C, S and r held fixed.
3. The addback matches in155_line_11, a reference that follows Schedule
   IN-155 lines 1 to 11 and the worksheet's cells L8 to L10.
4. vt_taxable_income >= 0, and does not depend on the 2018+ Vermont base
   (vt_agi, vt_standard_deduction, vt_personal_exemptions).
5. Raising the other additions by d raises vt_taxable_income by between 0
   and d, and by exactly d when the original value is positive.

Properties 4 and 5 fail if 2017 uses the 2018+ formula, which ignores the
additions and reads the Vermont base. The model computes in single
precision, so comparisons allow one cent or eight float32 spacings.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2017
MAX_AMOUNT = 100_000
SETTINGS = settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

amount = st.integers(min_value=0, max_value=MAX_AMOUNT)


def tolerance(*amounts):
    scale = np.float32(max(np.max(np.abs(a)) for a in amounts))
    return max(0.01, 8 * float(np.spacing(scale)))


def calculate(units, variable):
    """One Vermont tax unit per household, each with its own inputs."""
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        people[f"p{i}"] = {"age": {YEAR: 40}}
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            **{name: {YEAR: value} for name, value in unit.items()},
        }
        households[f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {YEAR: "VT"},
        }
    situation = {
        "people": people,
        "tax_units": tax_units,
        "households": households,
    }
    return Simulation(situation=situation).calculate(variable, YEAR)


def complete_addback_unit(draw):
    """Build total itemized deductions from their parts, and draw the section
    68 reduction within its ceiling: 80% of the deductions it limits."""
    unit = dict(draw)
    unit["total_itemized_taxable_income_deductions"] = total = (
        unit["salt_deduction"]
        + unit["medical_expense_deduction"]
        + unit["charitable_deduction"]
        + unit.pop("other_itemized")
    )
    ceiling = 0.8 * max(total - unit["medical_expense_deduction"], 0)
    reduction = round(unit.pop("reduction_share") * ceiling)
    unit["itemized_taxable_income_deductions_reduction"] = reduction
    unit["itemized_taxable_income_deductions"] = total - reduction
    return unit


addback_unit = st.fixed_dictionaries(
    {
        "tax_unit_itemizes": st.booleans(),
        "other_itemized": amount,
        "reduction_share": st.sampled_from([0, 0.25, 0.5, 1]),
        "wagering_losses_deduction": st.one_of(st.just(0), amount),
        "standard_deduction": st.integers(min_value=0, max_value=20_000),
        "salt_deduction": amount,
        "state_withheld_income_tax": amount,
        "local_income_tax": st.just(0),
        "state_sales_tax": amount,
        "local_sales_tax": st.just(0),
        "medical_expense_deduction": amount,
        "charitable_deduction": amount,
    }
).map(complete_addback_unit)


def itemized_total(unit):
    return (
        unit["itemized_taxable_income_deductions"] + unit["wagering_losses_deduction"]
    )


def in155_line_11(unit):
    """The 2017 Schedule IN-155 addback, line by line, with the Department's
    worksheet for limited itemized deductions on lines 4 and 6."""
    if not unit["tax_unit_itemizes"]:
        return 0.0
    # Worksheet: L8 total deductions, L9 deductions not limited at the
    # federal level (medical and wagering losses here), L10 total deductions
    # after limitations.
    l8 = (
        unit["total_itemized_taxable_income_deductions"]
        + unit["wagering_losses_deduction"]
    )
    l9 = unit["medical_expense_deduction"] + unit["wagering_losses_deduction"]
    l10 = itemized_total(unit)
    ratio = (l10 - l9) / (l8 - l9) if l8 > l9 else 1.0
    # Schedule A line 5a holds income taxes only when the filer elects them
    # over sales taxes.
    income_taxes = unit["state_withheld_income_tax"] + unit["local_income_tax"]
    sales_taxes = unit["state_sales_tax"] + unit["local_sales_tax"]
    schedule_a_5a = (
        min(income_taxes, unit["salt_deduction"]) if income_taxes >= sales_taxes else 0
    )
    line_1 = itemized_total(unit)  # Schedule A line 29
    line_2 = unit["standard_deduction"]
    # A filer whose itemized deductions are below the standard deduction has
    # nothing to add back on line 3.
    line_3 = max(line_1 - line_2, 0)
    line_4 = schedule_a_5a * ratio
    line_5 = unit["medical_expense_deduction"]
    line_6 = unit["charitable_deduction"] * ratio
    line_7 = line_4 + line_5 + line_6
    line_8 = line_1 - line_7
    line_9 = line_2 * 2.5
    line_10 = max(line_8 - line_9, 0)
    return min(line_3, line_4) + line_10


@SETTINGS
@given(units=st.lists(addback_unit, min_size=1, max_size=20), raise_by=amount)
def test_addback_bounds_and_monotonicity(units, raise_by):
    addback = calculate(units, "vt_2017_itemized_deduction_addback")
    itemized = np.array([itemized_total(u) for u in units])
    standard = np.array([u["standard_deduction"] for u in units])
    itemizes = np.array([u["tax_unit_itemizes"] for u in units])
    upper = np.maximum(itemized - standard, 0) + np.maximum(
        itemized - 2.5 * standard, 0
    )
    eps = tolerance(addback, upper)
    assert np.all(addback >= -eps)
    assert np.all(addback <= upper + eps)
    assert np.all(np.abs(addback[~itemizes]) <= eps)
    # Scaled income taxes are at most the SALT deduction, so the other
    # deductions are at least I - SALT - M - C.
    salt = np.array([u["salt_deduction"] for u in units])
    medical = np.array([u["medical_expense_deduction"] for u in units])
    charitable = np.array([u["charitable_deduction"] for u in units])
    lower = np.maximum(itemized - salt - medical - charitable - 2.5 * standard, 0)
    assert np.all(addback[itemizes] >= lower[itemizes] - eps)

    raised = [
        {
            **u,
            "itemized_taxable_income_deductions": u[
                "itemized_taxable_income_deductions"
            ]
            + raise_by,
        }
        for u in units
    ]
    raised_addback = calculate(raised, "vt_2017_itemized_deduction_addback")
    assert np.all(raised_addback >= addback - tolerance(addback, raised_addback))


@SETTINGS
@given(units=st.lists(addback_unit, min_size=1, max_size=20))
def test_addback_matches_schedule_in155(units):
    addback = calculate(units, "vt_2017_itemized_deduction_addback")
    expected = np.array([in155_line_11(u) for u in units])
    assert np.all(np.abs(addback - expected) <= tolerance(addback, expected))


taxable_income_unit = st.fixed_dictionaries(
    {
        "adjusted_gross_income": st.integers(min_value=-20_000, max_value=MAX_AMOUNT),
        "exemptions": st.integers(min_value=0, max_value=20_000),
        "taxable_income_deductions": st.integers(min_value=0, max_value=50_000),
        "vt_2017_itemized_deduction_addback": st.integers(
            min_value=0, max_value=20_000
        ),
        "vt_2017_other_additions": st.integers(min_value=0, max_value=20_000),
        "vt_2017_subtractions": st.integers(min_value=0, max_value=20_000),
        "vt_agi": amount,
        "vt_standard_deduction": st.integers(min_value=0, max_value=20_000),
        "vt_personal_exemptions": st.integers(min_value=0, max_value=20_000),
    }
)


@SETTINGS
@given(
    units=st.lists(taxable_income_unit, min_size=1, max_size=20),
    vermont_base_shift=st.integers(min_value=1, max_value=50_000),
    raise_by=st.integers(min_value=1, max_value=20_000),
)
def test_taxable_income_floor_base_and_additions(units, vermont_base_shift, raise_by):
    taxable = calculate(units, "vt_taxable_income")
    assert np.all(taxable >= 0)

    shifted = [{**u, "vt_agi": u["vt_agi"] + vermont_base_shift} for u in units]
    shifted_taxable = calculate(shifted, "vt_taxable_income")
    assert np.all(
        np.abs(shifted_taxable - taxable) <= tolerance(taxable, shifted_taxable)
    )

    raised = [
        {
            **u,
            "vt_2017_other_additions": u["vt_2017_other_additions"] + raise_by,
        }
        for u in units
    ]
    raised_taxable = calculate(raised, "vt_taxable_income")
    change = raised_taxable - taxable
    eps = tolerance(taxable, raised_taxable)
    assert np.all(change >= -eps)
    assert np.all(change <= raise_by + eps)
    positive = taxable > eps
    assert np.all(np.abs(change[positive] - raise_by) <= eps)
