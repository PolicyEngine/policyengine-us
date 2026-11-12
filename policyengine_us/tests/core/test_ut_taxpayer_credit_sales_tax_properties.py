"""Check Utah's taxpayer credit across deductions and federal tax elections.

Utah Code 59-10-1018 removes state or local income tax from the federal
itemized total. From 2018 through 2025, claimants subtract the income tax
paid and reported, up to $10,000. Before 2018 and from 2026, claimants
subtract only the income tax allowed in their federal itemized deductions.

The draws vary the SALT phase-down, all five filing statuses, and supplied
federal itemized totals after a reduction of up to 80%. Each simulation
holds every drawn unit twice, with the second unit electing sales tax.

1. Sales-tax electors keep their supplied federal itemized total. When no
   positive total enters the simulation, they keep non-SALT deductions plus
   the allowed SALT deduction.
2. Income-tax electors subtract the amount for the applicable statutory
   edition. The base never exceeds the effective total or falls more than
   $10,000 below it from 2018 through 2025; outside those years it stays
   between zero and the effective total.
3. Raising sales tax above income tax never lowers the base, including
   when section 68 reduces the supplied federal itemized total.

The paired, vectorized simulations check these properties over inputs that
single-household policy examples cannot exhaust. The random reductions
exercise the allocation independently of the federal section 68 formula;
the YAML tests also calculate actual section 68 reductions.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2017, 2018, 2024, 2025, 2026)
FILING_STATUSES = (
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)
AMOUNT = st.integers(min_value=0, max_value=60_000)

UNIT = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(FILING_STATUSES),
        "charitable": AMOUNT,
        "real_estate": AMOUNT,
        "income_tax": AMOUNT,
        "sales_tax": AMOUNT,
        "extra_itemized": AMOUNT,
        "magi": st.integers(min_value=0, max_value=800_000),
        "section_68_cut": st.integers(min_value=0, max_value=80),
        "supply_itemized": st.booleans(),
    }
)


def _salt_cap(unit, year):
    # 26 U.S.C. 164(b)(6)-(7): halve the separate-filer maximum,
    # threshold, floor and phase-down reduction.
    full = {
        2017: np.inf,
        2018: 10_000,
        2024: 10_000,
        2025: 40_000,
        2026: 40_400,
    }[year]
    fraction = 0.5 if unit["filing_status"] == "SEPARATE" else 1
    if year < 2025:
        return full * fraction
    threshold = {2025: 500_000, 2026: 505_000}[year] * fraction
    reduction = 0.3 * max(0, unit["magi"] - threshold) * fraction
    return max(10_000 * fraction, full * fraction - reduction)


def _salt(unit, year):
    return min(
        unit["real_estate"] + max(unit["income_tax"], unit["sales_tax"]),
        _salt_cap(unit, year),
    )


def _reconstructed(unit, year):
    return unit["charitable"] + unit["extra_itemized"] + _salt(unit, year)


def _itemized(unit, year):
    if not unit["supply_itemized"]:
        return 0
    total = _reconstructed(unit, year)
    # Round the amount removed from the total down to whole dollars.
    return total - total * unit["section_68_cut"] // 100


def _situation(year, units):
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        name = f"p{i}"
        people[name] = {
            "age": {period: 40},
            "real_estate_taxes": {period: unit["real_estate"]},
            "investment_interest_expense": {period: 0},
        }
        tax_units[f"t{i}"] = {
            "members": [name],
            "filing_status": {period: unit["filing_status"]},
            "tax_unit_itemizes": {period: True},
            "charitable_deduction": {period: unit["charitable"]},
            "interest_deduction": {period: unit["extra_itemized"]},
            "medical_expense_deduction": {period: 0},
            "casualty_loss_deduction": {period: 0},
            "misc_deduction": {period: 0},
            "agi_plus_section_911_931_933_exclusions": {period: unit["magi"]},
            "state_withheld_income_tax": {period: unit["income_tax"]},
            "local_income_tax": {period: 0},
            "state_sales_tax": {period: unit["sales_tax"]},
            "local_sales_tax": {period: 0},
            "salt_deduction": {period: _salt(unit, year)},
            "itemized_taxable_income_deductions": {period: _itemized(unit, year)},
        }
        households[f"h{i}"] = {"members": [name], "state_code": {period: "UT"}}
    return {"people": people, "tax_units": tax_units, "households": households}


def _with_sales_election(unit):
    return {**unit, "sales_tax": unit["income_tax"] + 1 + unit["sales_tax"]}


def _unit(**overrides):
    return {
        "filing_status": "JOINT",
        "charitable": 6_000,
        "real_estate": 4_000,
        "income_tax": 9_000,
        "sales_tax": 2_000,
        "extra_itemized": 0,
        "magi": 0,
        "section_68_cut": 10,
        "supply_itemized": True,
        **overrides,
    }


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
@example(year=2017, units=[_unit(filing_status=s) for s in FILING_STATUSES])
@example(year=2018, units=[_unit(real_estate=10_000, income_tax=8_000)])
@example(year=2024, units=[_unit(real_estate=10_000, income_tax=8_000)])
@example(
    year=2025,
    units=[_unit(real_estate=5_000, income_tax=30_000, magi=600_000)],
)
@example(
    year=2026,
    units=[
        _unit(real_estate=0, income_tax=0, sales_tax=9_000),
        _unit(),
        _unit(real_estate=25_000, income_tax=30_000, magi=605_000),
        _unit(
            filing_status="SEPARATE",
            real_estate=5_000,
            income_tax=20_000,
            magi=300_000,
        ),
    ],
)
def test_utah_credit_base_keeps_sales_tax(year, units):
    paired = units + [_with_sales_election(unit) for unit in units]
    sim = Simulation(situation=_situation(year, paired))
    base = sim.calculate("ut_federal_deductions_for_taxpayer_credit", year)
    itemized = np.array([_itemized(unit, year) for unit in paired])
    salt = np.array([_salt(unit, year) for unit in paired])
    reconstructed = np.array([_reconstructed(unit, year) for unit in paired])
    effective = np.where(itemized > 0, itemized, reconstructed)
    sales_elected = np.array([u["sales_tax"] > u["income_tax"] for u in paired])

    # (1) Sales-tax electors keep the effective federal itemized total.
    assert np.allclose(base[sales_elected], effective[sales_elected])

    # (2) Income-tax electors subtract only the dated statutory amount.
    income = ~sales_elected
    raw_income = np.array([unit["income_tax"] for unit in paired])
    if 2018 <= year <= 2025:
        excluded_income = np.minimum(raw_income, 10_000)
    else:
        real_estate = np.array([unit["real_estate"] for unit in paired])
        deducted_income = np.maximum(0, salt - real_estate)
        # The draws contain no section 68(c) protected deductions, so each
        # dollar of the income-tax deduction retains the same fraction.
        retained = np.divide(
            itemized,
            reconstructed,
            out=np.ones_like(itemized, dtype=float),
            where=(itemized > 0) & (reconstructed > 0),
        )
        excluded_income = np.minimum(raw_income, deducted_income * retained)
    expected_income_base = effective - excluded_income
    lower_bound = effective - 10_000 if 2018 <= year <= 2025 else 0
    assert np.all(
        base[income] >= np.broadcast_to(lower_bound, base.shape)[income] - 0.03
    )
    assert np.all(base[income] <= effective[income] + 0.03)
    assert np.allclose(base[income], expected_income_base[income], rtol=1e-6, atol=0.03)

    # (3) Moving to a sales-tax election never lowers the base, including
    # pairs whose supplied itemized totals include a section 68 reduction.
    n = len(units)
    assert np.all(base[n:] >= base[:n] - 0.03)
