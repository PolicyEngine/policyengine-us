"""Property tests: Vermont's 2017 taxable income under former 32 V.S.A.
§ 5811(21).

For 2017, Vermont taxable income is federal taxable income, before its zero
floor, plus the itemized deduction addback and other additions, less the
subtractions, floored at zero. For allowed federal itemized deductions I,
deducted income taxes T, medical M, charitable C and federal standard
deduction S, the addback is min(T, max(I - S, 0)) + max(I - T - M - C -
2.5 S, 0) for an itemizer and zero otherwise.

Properties checked, each in one batched simulation per example:

1. 0 <= addback <= max(I - S, 0) + max(I - 2.5 S, 0), and the addback is zero
   for a nonitemizer.
2. The addback never falls when I rises with T, M, C and S held fixed.
3. vt_taxable_income >= 0, and does not depend on the 2018+ Vermont base
   (vt_agi, vt_standard_deduction, vt_personal_exemptions).
4. Raising the other additions by d raises vt_taxable_income by between 0
   and d, and by exactly d when the original value is positive.

Properties 3 and 4 fail if 2017 uses the 2018+ formula, which ignores the
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


addback_unit = st.fixed_dictionaries(
    {
        "tax_unit_itemizes": st.booleans(),
        "itemized_taxable_income_deductions": amount,
        "standard_deduction": st.integers(min_value=0, max_value=20_000),
        "salt_deduction": amount,
        "state_withheld_income_tax": amount,
        "local_income_tax": st.just(0),
        "state_sales_tax": amount,
        "local_sales_tax": st.just(0),
        "medical_expense_deduction": amount,
        "charitable_deduction": amount,
    }
)


@SETTINGS
@given(units=st.lists(addback_unit, min_size=1, max_size=20), raise_by=amount)
def test_addback_bounds_and_monotonicity(units, raise_by):
    addback = calculate(units, "vt_2017_itemized_deduction_addback")
    itemized = np.array([u["itemized_taxable_income_deductions"] for u in units])
    standard = np.array([u["standard_deduction"] for u in units])
    itemizes = np.array([u["tax_unit_itemizes"] for u in units])
    upper = np.maximum(itemized - standard, 0) + np.maximum(
        itemized - 2.5 * standard, 0
    )
    eps = tolerance(addback, upper)
    assert np.all(addback >= -eps)
    assert np.all(addback <= upper + eps)
    assert np.all(np.abs(addback[~itemizes]) <= eps)

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
