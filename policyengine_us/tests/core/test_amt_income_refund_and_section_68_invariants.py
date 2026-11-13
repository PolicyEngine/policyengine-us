"""Alternative minimum taxable income leaves out tax refunds and section 68.

26 U.S.C. 56(b)(1)(C): no recovery of a state or local tax is in alternative
minimum taxable income (Form 6251 line 2b). 56(b)(1)(E): section 68 does not
apply. Each Hypothesis example evaluates a batch of tax units, and their twins
without the refund, in one vectorized simulation in a state with no income
tax. With the itemization choice fixed, the households have no deduction that
depends on AGI once the AMT add-backs are made: no medical expenses and no
charitable gifts. From 2026 the 0.5% floor of 26 U.S.C. 170(b)(1)(I) ties the
charitable deduction to AGI, so a refund rightly raises AMTI by 0.5% of it.

Two properties, for 2017 (the old section 68), 2025 (no section 68) and 2026
(the P.L. 119-21 section 68), single, joint and married filing separately,
itemizing or not. The drawn households rarely reach section 68 or the separate
filer's increase, so a fixed example pins households that do in each year:
itemizers above the 2017 and 2026 section 68 thresholds, and separate filers
inside the 2025 and 2026 increase bands.

1. Refund invariance: adding a filer's state tax refund leaves AMTI unchanged.
   The refund enters AGI and comes back out, and any change it causes in the
   section 68 reduction or the capped SALT deduction cancels, because AMTI
   reverses the first and adds back the second. For a separate filer, the
   55(d)(2) increase is figured on AMTI without the refund, so it holds too.
2. Statutory identity: AMTI before that separate filer increase is AGI, less
   the refund, less the itemized deductions the AMT allows. Those are all
   itemized deductions before section 68 except taxes and miscellaneous
   deductions (56(b)(1)(A)), and none for a filer who takes the standard
   deduction (56(b)(1)(D)). This checks the formula's route through taxable
   income against the statute's definition.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# The model computes in float32: allow about two units in the last place.
TOLERANCE = dict(atol=0.01, rtol=2.5e-7)


@st.composite
def tax_unit(draw):
    return {
        "status": draw(st.sampled_from(["SINGLE", "JOINT", "SEPARATE"])),
        "itemizes": draw(st.booleans()),
        "employment_income": draw(st.integers(20_000, 3_000_000)),
        "salt_refund_income": draw(st.integers(1, 20_000)),
        "real_estate_taxes": draw(st.integers(0, 40_000)),
        "home_mortgage_interest": draw(st.integers(0, 40_000)),
    }


# Itemizers above the 2017 and 2026 section 68 thresholds, a separate filer
# whose AMTI (700,000) is inside the 2026 increase band (over 640,200) and
# below the 2025 one, and one (950,000) inside the 2025 band (over 900,350)
# and above the 2026 cap.
BOUNDARY_UNITS = [
    dict(
        status="SINGLE",
        itemizes=True,
        employment_income=2_000_000,
        salt_refund_income=5_000,
        real_estate_taxes=12_000,
        home_mortgage_interest=30_000,
    ),
    dict(
        status="JOINT",
        itemizes=True,
        employment_income=3_000_000,
        salt_refund_income=8_000,
        real_estate_taxes=20_000,
        home_mortgage_interest=40_000,
    ),
    dict(
        status="SEPARATE",
        itemizes=False,
        employment_income=700_000,
        salt_refund_income=10_000,
        real_estate_taxes=0,
        home_mortgage_interest=0,
    ),
    dict(
        status="SEPARATE",
        itemizes=False,
        employment_income=950_000,
        salt_refund_income=20_000,
        real_estate_taxes=0,
        home_mortgage_interest=0,
    ),
]


def _simulate(units, year):
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for twin in (0, 1):
        for i, unit in enumerate(units):
            head = f"head_{twin}_{i}"
            members = [head]
            situation["people"][head] = {
                "age": {year: 45},
                "employment_income": {year: unit["employment_income"]},
                "salt_refund_income": {
                    year: unit["salt_refund_income"] if twin == 0 else 0
                },
                "real_estate_taxes": {year: unit["real_estate_taxes"]},
                "home_mortgage_interest": {year: unit["home_mortgage_interest"]},
            }
            if unit["status"] == "JOINT":
                spouse = f"spouse_{twin}_{i}"
                situation["people"][spouse] = {"age": {year: 45}}
                members.append(spouse)
            situation["tax_units"][f"unit_{twin}_{i}"] = {
                "members": members,
                "filing_status": {year: unit["status"]},
                "tax_unit_itemizes": {year: unit["itemizes"]},
            }
            situation["households"][f"household_{twin}_{i}"] = {
                "members": members,
                "state_code": {year: "TX"},
            }
    return Simulation(situation=situation)


@pytest.mark.parametrize("year", [2017, 2025, 2026])
@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(units=st.lists(tax_unit(), min_size=8, max_size=8))
@example(units=BOUNDARY_UNITS)
def test_amt_income_leaves_out_refunds_and_section_68(year, units):
    simulation = _simulate(units, year)

    def calc(variable):
        return np.asarray(simulation.calculate(variable, year), dtype=float)

    n = len(units)
    amti = calc("amt_income")

    # 1. Refund invariance: each unit matches its twin without the refund.
    np.testing.assert_allclose(amti[:n], amti[n:], **TOLERANCE)

    # 2. Statutory identity, before the separate filer increase: AGI less the
    # refund less the AMT's itemized deductions (before section 68, without
    # taxes and miscellaneous ones).
    refunds = np.array([unit["salt_refund_income"] for unit in units] + [0] * n)
    allowed_itemized = np.where(
        calc("tax_unit_itemizes").astype(bool),
        calc("total_itemized_taxable_income_deductions")
        - calc("salt_deduction")
        - calc("misc_deduction"),
        0,
    )
    np.testing.assert_allclose(
        calc("amt_income_before_separate_addition"),
        calc("adjusted_gross_income") - refunds - allowed_itemized,
        **TOLERANCE,
    )
