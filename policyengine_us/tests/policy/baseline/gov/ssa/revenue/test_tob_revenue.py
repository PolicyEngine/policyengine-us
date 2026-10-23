"""Generated TOB split invariants and branch cache isolation.

Policy examples and independent tax calculations live in the variable YAML
files. Python is needed to quantify the split invariants over generated
inputs and to exercise calculation order on an already populated cache.
Each generated batch combines eight income/donation draws with fixed
boundary and signed-allocation witnesses. Five filing profiles cover
single, joint, separate living together, separate living apart, and an
elderly single person electing to itemize. Cash gifts and tax-exempt
interest exercise binding charitable limits and elderly-credit changes.
Charitable gifts are the sole itemized deductions; deductible medical
expenses (including Medicare premiums) and state/local taxes are excluded.
One vectorized simulation shares the expensive counterfactual setup across
the batch. Joint benefits and interest are divided between spouses to
exercise tax-unit aggregation.
"""

from itertools import product

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


PROFILES = (
    ("SINGLE", False, False),
    ("JOINT", True, False),
    ("SEPARATE", True, False),
    ("SEPARATE", False, False),
    ("SINGLE", False, True),
)
# Keep the former standalone Hypothesis examples in each vectorized batch,
# avoiding three additional full-model constructions. The last two cases
# release charitable deductions and elderly credits as inclusion rises;
# they cover negative OASDI and negative HI without the MFS credit base.
FIXED_CASES = (
    (20_000, 30_000, 0, 0),
    (0, 0, 0, 0),
    (60_000, 300_000, 0, 0),
    (1_000, 11_500, 20_000, 20_000),
    (1_000, 11_500, 23_000, 20_000),
)
REVENUE_VARIABLES = (
    "tob_revenue_oasdi",
    "tob_revenue_medicare_hi",
    "tob_revenue_total",
)


def simulation(cases, age, year, force_itemization=True):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "spm_units",
            "families",
        )
    }
    for i, (case, profile) in enumerate(product(cases, PROFILES)):
        benefits, interest, exempt_interest, donations = case
        filing_status, cohabitating, itemizes = profile
        joint = filing_status == "JOINT"
        members = [f"head{i}"] + ([f"spouse{i}"] if joint else [])
        for j, member in enumerate(members):
            situation["people"][member] = {
                "age": {year: 67 if itemizes else age},
                "tax_unit_role_input": {year: "HEAD" if j == 0 else "SPOUSE"},
                "social_security": {year: benefits / len(members)},
                "taxable_interest_income": {year: interest / len(members)},
                "tax_exempt_interest_income": {year: exempt_interest / len(members)},
                "charitable_cash_donations": {year: donations / len(members)},
            }
        situation["tax_units"][f"tax_unit{i}"] = {
            "members": members,
            "filing_status": {year: filing_status},
            "cohabitating_spouses": {year: cohabitating},
            "itemized_medical_expenses": {year: 0},
            "salt_deduction": {year: 0},
        }
        if force_itemization:
            situation["tax_units"][f"tax_unit{i}"]["tax_unit_itemizes"] = {
                year: itemizes
            }
        situation["households"][f"household{i}"] = {
            "members": members,
            "state_name": {year: "TX"},
        }
        # Missing group entities default to one group containing everyone,
        # so define each explicitly to keep these households independent.
        for entity in ("marital_units", "spm_units", "families"):
            situation[entity][f"unit{i}"] = {"members": members}
        # These childless units do not participate in TANF. Supplying this
        # avoids unrelated monthly benefit calculations in tax branches.
        situation["spm_units"][f"unit{i}"]["takes_up_tanf_if_eligible"] = {year: False}
    return Simulation(situation=situation)


def check_invariants(sim, year, order=REVENUE_VARIABLES):
    taxable_ss = sim.calculate("tax_unit_taxable_social_security", year).copy()
    old_law_ss = sim.calculate("tax_unit_taxable_social_security_pre_1993", year)
    result = {name: sim.calculate(name, year).copy() for name in order}
    oasdi, hi, total = (result[name] for name in REVENUE_VARIABLES)
    # Float32 tax subtraction can lose a few mills at the upper generated
    # income bound; no policy difference of a cent is tolerated.
    tolerance = 0.01
    np.testing.assert_allclose(oasdi + hi, total, rtol=0, atol=tolerance)
    # Revenue differences are signed: deductions and credits can make tax
    # fall as inclusion rises. Equal counterfactual inclusions still imply
    # equal taxes, even for those households.
    np.testing.assert_allclose(oasdi[old_law_ss == 0], 0, rtol=0, atol=tolerance)
    np.testing.assert_allclose(hi[old_law_ss == taxable_ss], 0, rtol=0, atol=tolerance)
    assert np.all(old_law_ss >= -tolerance)
    assert np.all(old_law_ss <= taxable_ss + tolerance)
    np.testing.assert_array_equal(
        sim.calculate("tax_unit_taxable_social_security", year), taxable_ss
    )
    # The formulas remove their temporary branches after calculation.
    assert not {
        "oasdi_no_ss",
        "oasdi_capped",
        "oasdi_pre_1993",
        "oasdi_old_law",
        "hi_capped",
        "tob_calc",
    }.intersection(sim.branches)
    return result


# Each generated draw exercises 65 tax units in three tax counterfactuals.
# Batching increases generated household coverage while reducing full-model
# branch clones; each draw still owns an independent simulation and caches.
@settings(max_examples=2, derandomize=True, deadline=None)
@given(
    cases=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=60_000),
            st.integers(min_value=0, max_value=300_000),
            st.integers(min_value=0, max_value=100_000),
            st.integers(min_value=0, max_value=300_000),
        ),
        min_size=8,
        max_size=8,
    ),
    age=st.sampled_from([60, 70]),
)
def test_generated_tob_split_invariants(cases, age):
    # The elderly-credit witnesses remain taxable in 2024. The 2026 senior
    # deduction can eliminate their tax; that year's counterfactual/cache
    # behavior is covered independently by the test below.
    year = 2024
    result = check_invariants(simulation([*cases, *FIXED_CASES], age, year), year)
    # Verify that the population actually exercises both kinds of signed
    # allocation rather than passing only on non-negative households.
    assert np.any(result["tob_revenue_oasdi"] < 0)
    assert np.any(result["tob_revenue_medicare_hi"] < 0)


def test_tob_split_preserves_inputs_and_cached_current_law_tax_in_either_order():
    year = 2026
    # Keep itemization endogenous here so branches must also invalidate and
    # recompute its cached choice, rather than preserve a fixed input.
    sim = simulation(FIXED_CASES, 70, year, force_itemization=False)
    # Populate the cache before creating counterfactual branches. If the
    # branches keep calculated AGI or tax arrays, the split can become zero.
    names = (
        "social_security",
        "taxable_interest_income",
        "tax_exempt_interest_income",
        "charitable_cash_donations",
        "tax_unit_itemizes",
        "itemized_medical_expenses",
        "salt_deduction",
        "tax_unit_taxable_social_security",
        "adjusted_gross_income",
        "income_tax",
    )
    original = {name: sim.calculate(name, year).copy() for name in names}
    first = check_invariants(sim, year)
    for name in REVENUE_VARIABLES:
        sim.delete_arrays(name)
    # Starting with HI also exercises HI -> total/OASDI dependencies.
    reverse = check_invariants(
        sim,
        year,
        ("tob_revenue_medicare_hi", "tob_revenue_total", "tob_revenue_oasdi"),
    )
    for name in REVENUE_VARIABLES:
        np.testing.assert_array_equal(reverse[name], first[name])
    for name in names:
        np.testing.assert_array_equal(sim.calculate(name, year), original[name])
