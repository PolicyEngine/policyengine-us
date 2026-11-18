"""Property tests: Maryland, Maine and New Mexico itemized deductions in 2026
carry the federal section 68 reduction (P.L. 119-21, sec. 70111).

Each state starts from the federal itemized deductions allowed after section
68. For a pre-reduction federal total T > 0 and reduction 0 <= R <= T, write
q = (T - R) / T. With every input drawn independently and R > 0, these hold:

1. Maryland (Tax-General 10-218(b)(1), (b)(3)), below its phaseout threshold:
   md_itemized_deductions = q * (non-SALT deductions + capped property
   taxes). This equals T - R - I + R * I / T for income taxes
   I = T - base, the pro rata restoration of 10-218(b)(3).
2. Maine (36 M.R.S. 5125(1)), with no SALT or medical deduction:
   me_itemized_deductions_pre_phaseout = min(T - R, cap).
3. New Mexico (NMSA 7-2-2(N)(2)): nm_itemized_deductions = T - R, and the
   SALT addback lies between zero and the excess of T - R over the standard
   deduction.

Each identity fails on main whenever R > 0, so none passes trivially: main
uses T (or the unreduced base) and ignores R. All households share one
simulation per example, which keeps the test to a few model builds.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
TOLERANCE = 0.05


def amount(low=0, high=60_000):
    return st.integers(min_value=low, max_value=high)


@st.composite
def unit(draw):
    base = draw(amount(1_000))
    income_tax = draw(amount(0, 30_000))
    total = base + income_tax
    # Section 68 reduction: up to 2/37 of the total, drawn positive.
    reduction = draw(st.integers(min_value=1, max_value=total * 2 // 37 + 1))
    return dict(
        base=base,
        income_tax=income_tax,
        total=total,
        reduction=min(reduction, total),
        standard=draw(amount(5_000, 40_000)),
    )


def build(units):
    people, tax_units, households = {}, {}, {}
    for state in ["MD", "ME", "NM"]:
        for i, u in enumerate(units):
            key = f"{state}{i}"
            people[key] = {"age": {YEAR: 40}}
            common = {
                "members": [key],
                "filing_status": {YEAR: "SINGLE"},
                "tax_unit_itemizes": {YEAR: True},
                "adjusted_gross_income": {YEAR: 100_000},
                "itemized_taxable_income_deductions_reduction": {YEAR: u["reduction"]},
                "medical_expense_deduction": {YEAR: 0},
            }
            if state == "MD":
                common.update(
                    total_itemized_taxable_income_deductions={YEAR: u["total"]},
                    itemized_deductions_less_salt={YEAR: u["base"]},
                    capped_property_taxes={YEAR: 0},
                    salt_deduction={YEAR: u["income_tax"]},
                )
            elif state == "ME":
                common.update(
                    total_itemized_taxable_income_deductions={YEAR: u["total"]},
                    itemized_deductions_less_salt={YEAR: u["total"]},
                    salt_deduction={YEAR: 0},
                    me_agi={YEAR: 50_000},
                )
            else:
                common.update(
                    total_itemized_taxable_income_deductions={YEAR: u["total"]},
                    itemized_deductions_less_salt={YEAR: u["base"]},
                    standard_deduction={YEAR: u["standard"]},
                    state_and_local_sales_or_income_tax={YEAR: u["income_tax"]},
                )
            tax_units[f"t{key}"] = common
            households[f"h{key}"] = {"members": [key], "state_code": {YEAR: state}}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(unit(), min_size=1, max_size=6))
def test_state_itemized_deductions_carry_section_68(units):
    n = len(units)
    sim = build(units)
    total = np.array([u["total"] for u in units], dtype=float)
    reduction = np.array([u["reduction"] for u in units], dtype=float)
    base = np.array([u["base"] for u in units], dtype=float)
    standard = np.array([u["standard"] for u in units], dtype=float)
    allowed = total - reduction
    q = allowed / total

    md = sim.calculate("md_itemized_deductions", YEAR)[:n]
    me = sim.calculate("me_itemized_deductions_pre_phaseout", YEAR)[n : 2 * n]
    nm = sim.calculate("nm_itemized_deductions", YEAR)[2 * n :]
    nm_add_back = sim.calculate("nm_salt_add_back", YEAR)[2 * n :]
    me_cap = sim.tax_benefit_system.parameters(
        YEAR
    ).gov.states.me.tax.income.deductions.itemized.cap

    # 1. Maryland: base scaled by q, the pro rata income-tax restoration.
    np.testing.assert_allclose(md, base * q, atol=TOLERANCE)
    assert np.all(md < base)
    # 2. Maine: the federally allowed total, capped.
    np.testing.assert_allclose(me, np.minimum(allowed, me_cap), atol=TOLERANCE)
    # 3. New Mexico: the allowed total, and an addback within its bounds.
    np.testing.assert_allclose(nm, allowed, atol=TOLERANCE)
    assert np.all(nm_add_back >= -TOLERANCE)
    assert np.all(nm_add_back <= np.maximum(allowed - standard, 0) + TOLERANCE)
