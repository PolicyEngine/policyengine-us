"""Generated populations check historical federal tax discontinuities.

The 2017 Form 1040 exemption worksheet, page 41, rounds each partial
$2,500 step upward ($1,250 for separate filers). Thus the deduction stays
constant inside a step and never increases when AGI increases. From 2018
the deduction remains suspended. These are intended statutory steps.

Before 2018, IRC 24(e)(1) permits a child's SSN, ITIN or ATIN. Holding a
valid TIN fixed, changing the child's SSN-card category cannot change the
2017 identification result. A child without any TIN does not qualify.

Each example contains a generated mixed population, which the YAML runner
cannot express. Individual and end-to-end source examples remain in YAML.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation

THRESHOLDS_2017 = {
    "SINGLE": 261_500,
    "JOINT": 313_800,
    "SEPARATE": 156_900,
    "HEAD_OF_HOUSEHOLD": 287_650,
    "SURVIVING_SPOUSE": 313_800,
}
SETTINGS = settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


@pytest.fixture(scope="module")
def system():
    return CountryTaxBenefitSystem()


@SETTINGS
@given(
    st.lists(
        st.tuples(
            st.sampled_from(list(THRESHOLDS_2017)),
            st.integers(1, 6),
            st.integers(0, 49),
            st.integers(1, 1_249),
        ),
        min_size=2,
        max_size=12,
    )
)
def test_exemption_steps_are_constant_and_nonincreasing(system, cases):
    people, units = {}, {}
    for i, (status, count, step_index, offset) in enumerate(cases):
        step = 1_250 if status == "SEPARATE" else 2_500
        start = THRESHOLDS_2017[status] + step * step_index
        incomes = (start, start + offset, start + step)
        for j, income in enumerate(incomes):
            name = f"person_{i}_{j}"
            people[name] = {"age": {2017: 40}}
            units[name] = {
                "members": [name],
                "filing_status": {2017: status},
                "adjusted_gross_income": {2017: income},
                "exemptions_count": {2017: count},
            }
    sim = Simulation(
        situation={"people": people, "tax_units": units}, tax_benefit_system=system
    )
    deductions = sim.calculate("exemptions", 2017).reshape(-1, 3)
    counts = np.array([case[1] for case in cases])
    assert np.isfinite(deductions).all()
    assert (deductions >= 0).all()
    assert (deductions <= 4_050 * counts[:, None]).all()
    assert (deductions[:, 0] >= deductions[:, 1]).all()
    np.testing.assert_allclose(deductions[:, 1], deductions[:, 2], atol=0.01, rtol=0)
    # A statutory reduction is an integer number of 2%-of-exemption steps.
    reductions = (4_050 * counts[:, None] - deductions) / (81 * counts[:, None])
    np.testing.assert_allclose(reductions, np.round(reductions), atol=0.0001, rtol=0)


@SETTINGS
@given(st.lists(st.booleans(), min_size=2, max_size=16))
def test_2017_child_identification_uses_tin_instead_of_ssn_category(system, has_tins):
    people = {}
    expected = []
    for i, has_tin in enumerate(has_tins):
        categories = (
            ("CITIZEN", "NON_CITIZEN_VALID_EAD", "OTHER_NON_CITIZEN", "NONE")
            if has_tin
            else ("NONE",)
        )
        for j, category in enumerate(categories):
            people[f"person_{i}_{j}"] = {
                "age": {2017: 8},
                "has_tin": {2017: has_tin},
                "ssn_card_type": {2017: category},
            }
            expected.append(has_tin)
    sim = Simulation(situation={"people": people}, tax_benefit_system=system)
    np.testing.assert_array_equal(
        sim.calculate("meets_ctc_child_identification_requirements", 2017), expected
    )


@pytest.mark.parametrize("year", range(2017, 2027))
@SETTINGS
@given(
    st.lists(
        st.tuples(
            st.integers(0, 20_000), st.integers(0, 30_000), st.integers(0, 100_000)
        ),
        min_size=2,
        max_size=10,
    ),
)
def test_employer_care_exclusion_and_credit_do_not_reuse_expenses(system, year, cases):
    """Form 2441 Part III reconciles the exclusion with the credit expense base."""
    people, units = {}, {}
    for i, (benefits, qualified, earnings) in enumerate(cases):
        head, child = f"head_{i}", f"child_{i}"
        people[head] = {
            "age": {year: 35},
            "is_tax_unit_head": {year: True},
            "dependent_care_employer_benefits": {year: benefits},
        }
        people[child] = {"age": {year: 8}, "is_tax_unit_dependent": {year: True}}
        units[f"unit_{i}"] = {
            "members": [head, child],
            "filing_status": {year: "SINGLE"},
            "cdcc_qualified_care_expenses": {year: qualified},
            "min_head_spouse_earned": {year: earnings},
        }
    sim = Simulation(
        situation={"people": people, "tax_units": units}, tax_benefit_system=system
    )
    exclusion = sim.calculate("dependent_care_assistance_exclusion", year)
    remaining = sim.calculate("cdcc_relevant_expenses", year)
    benefits, qualified, earnings = np.array(cases).T
    assert np.isfinite(exclusion).all() and np.isfinite(remaining).all()
    assert (exclusion >= 0).all() and (remaining >= 0).all()
    assert (exclusion <= benefits + 0.01).all()
    assert (exclusion <= earnings + 0.01).all()
    assert (remaining <= earnings + 0.01).all()
    assert (exclusion + remaining <= qualified + 0.01).all()
