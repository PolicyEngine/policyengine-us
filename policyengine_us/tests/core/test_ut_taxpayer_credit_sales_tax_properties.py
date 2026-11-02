"""Properties of the federal deductions in Utah's taxpayer credit base.

Utah Code 59-10-1018(1)(f)(i) starts from the federal itemized deductions
and removes only state or local income tax. A tax unit whose sales taxes
strictly exceed its income taxes takes the sales tax under the federal
formula (state_and_local_sales_or_income_tax is the larger of the two), so:

1. Sales-tax election: nothing is removed. The base equals the larger of the
   federal itemized total and the non-SALT itemized deductions plus the
   allowed SALT deduction, so it is never below either.
2. Income-tax election: the base never exceeds the larger of the federal
   itemized total and the non-SALT deductions plus capped real-estate tax,
   and it never falls below the latter.
3. Raising sales tax above income tax, with every other input fixed, never
   lowers the base.

Before this change (1) and (3) failed whenever the allowed SALT deduction
exceeded capped real-estate taxes: the sales tax was removed from the base.
Each example builds one small household simulation holding every drawn tax
unit twice, once as drawn and once with sales tax raised above income tax.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2018, 2024, 2025, 2026)
FILING_STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD")
AMOUNT = st.integers(min_value=0, max_value=60_000)

UNIT = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(FILING_STATUSES),
        "charitable": AMOUNT,
        "real_estate": AMOUNT,
        "income_tax": AMOUNT,
        "sales_tax": AMOUNT,
        "extra_itemized": AMOUNT,
        "supply_itemized": st.booleans(),
    }
)


def _salt_cap(filing_status, year):
    # 26 U.S.C. 164(b)(6) and (b)(7) caps before any phase-down: $10,000
    # ($5,000 separate) through 2024, $40,000 ($20,000) in 2025 and
    # $40,400 ($20,200) in 2026.
    full = {2018: 10_000, 2024: 10_000, 2025: 40_000, 2026: 40_400}[year]
    return full / 2 if filing_status == "SEPARATE" else full


def _situation(year, units):
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        name = f"p{i}"
        people[name] = {
            "age": {period: 40},
            "real_estate_taxes": {period: unit["real_estate"]},
        }
        salt = min(
            unit["real_estate"] + max(unit["income_tax"], unit["sales_tax"]),
            _salt_cap(unit["filing_status"], year),
        )
        itemized = (
            unit["charitable"] + salt + unit["extra_itemized"]
            if unit["supply_itemized"]
            else 0
        )
        tax_units[f"t{i}"] = {
            "members": [name],
            "filing_status": {period: unit["filing_status"]},
            "tax_unit_itemizes": {period: True},
            "charitable_deduction": {period: unit["charitable"]},
            "interest_deduction": {period: 0},
            "medical_expense_deduction": {period: 0},
            "casualty_loss_deduction": {period: 0},
            "misc_deduction": {period: 0},
            "state_withheld_income_tax": {period: unit["income_tax"]},
            "local_income_tax": {period: 0},
            "state_sales_tax": {period: unit["sales_tax"]},
            "local_sales_tax": {period: 0},
            "salt_deduction": {period: salt},
            "itemized_taxable_income_deductions": {period: itemized},
        }
        households[f"h{i}"] = {"members": [name], "state_code": {period: "UT"}}
    return {"people": people, "tax_units": tax_units, "households": households}


def _with_sales_election(unit):
    return {**unit, "sales_tax": unit["income_tax"] + 1 + unit["sales_tax"]}


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    year=st.sampled_from(YEARS),
    units=st.lists(UNIT, min_size=4, max_size=12),
)
def test_utah_credit_base_keeps_sales_tax(year, units):
    paired = units + [_with_sales_election(unit) for unit in units]
    situation = _situation(year, paired)
    sim = Simulation(situation=situation)
    base = sim.calculate("ut_federal_deductions_for_taxpayer_credit", year)
    period = str(year)
    tu = situation["tax_units"]
    itemized = np.array(
        [
            tu[f"t{i}"]["itemized_taxable_income_deductions"][period]
            for i in range(len(paired))
        ]
    )
    salt = np.array([tu[f"t{i}"]["salt_deduction"][period] for i in range(len(paired))])
    other = np.array([u["charitable"] for u in paired])
    real_estate = np.array([u["real_estate"] for u in paired])
    cap = np.array([_salt_cap(u["filing_status"], year) for u in paired])
    sales_elected = np.array([u["sales_tax"] > u["income_tax"] for u in paired])

    # (1) Sales-tax election removes nothing.
    sales_base = np.maximum(itemized, other + salt)
    assert np.allclose(base[sales_elected], sales_base[sales_elected])

    # (2) Income-tax election stays within its bounds.
    income_floor = other + np.minimum(real_estate, cap)
    income = ~sales_elected
    assert np.all(base[income] >= income_floor[income] - 1e-6)
    assert np.all(base[income] <= np.maximum(itemized, income_floor)[income] + 1e-6)

    # (3) Moving to a sales-tax election never lowers the base.
    n = len(units)
    assert np.all(base[n:] >= base[:n] - 1e-6)
