"""Generated TOB split invariants and branch cache isolation.

Policy examples and independent tax calculations live in the variable YAML
files. Python is needed to quantify the split invariants over generated
inputs and to exercise calculation order on an already populated cache.
Each example has four tax units in one vectorized simulation: single,
joint, separate living together, and separate living apart. Joint benefits
and interest are divided between spouses to exercise tax-unit aggregation.
"""

import numpy as np
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


PROFILES = (("SINGLE", False), ("JOINT", True), ("SEPARATE", True), ("SEPARATE", False))
REVENUE_VARIABLES = (
    "tob_revenue_oasdi",
    "tob_revenue_medicare_hi",
    "tob_revenue_total",
)


def simulation(benefits, interest, age, year):
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
    for i, (filing_status, cohabitating) in enumerate(PROFILES):
        joint = filing_status == "JOINT"
        members = [f"head{i}"] + ([f"spouse{i}"] if joint else [])
        for j, member in enumerate(members):
            situation["people"][member] = {
                "age": {year: age},
                "tax_unit_role_input": {year: "HEAD" if j == 0 else "SPOUSE"},
                "social_security": {year: benefits / len(members)},
                "taxable_interest_income": {year: interest / len(members)},
            }
        situation["tax_units"][f"tax_unit{i}"] = {
            "members": members,
            "filing_status": {year: filing_status},
            "cohabitating_spouses": {year: cohabitating},
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
    assert np.all(oasdi >= -tolerance)
    assert np.all(hi >= -tolerance)
    assert np.all(oasdi <= total + tolerance)
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


@settings(max_examples=20, derandomize=True, deadline=None)
@example(benefits=20_000, interest=30_000, age=70, year=2026)
@example(benefits=0, interest=0, age=60, year=2024)
@example(benefits=60_000, interest=300_000, age=70, year=2026)
@given(
    benefits=st.integers(min_value=0, max_value=60_000),
    interest=st.integers(min_value=0, max_value=300_000),
    age=st.sampled_from([60, 70]),
    year=st.sampled_from([2024, 2026]),
)
def test_generated_tob_split_invariants(benefits, interest, age, year):
    check_invariants(simulation(benefits, interest, age, year), year)


def test_tob_split_preserves_inputs_and_cached_current_law_tax_in_either_order():
    year = 2026
    sim = simulation(20_000, 30_000, 70, year)
    # Populate the cache before creating counterfactual branches. If the
    # branches keep calculated AGI or tax arrays, the split can become zero.
    names = (
        "social_security",
        "taxable_interest_income",
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
