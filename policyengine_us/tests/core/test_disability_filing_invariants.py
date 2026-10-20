"""Differential properties for taxable disability and the filing worksheets.

The merge review's seeded checks become Hypothesis batches, each calculated
in one simulation for 2024-2026 with a shared, unreformed system. YAML covers
the named households; this test checks independent worksheet references over
generated combinations of disability splits, wages, business profits/losses,
interest, claimability, age and blindness. It does not read model parameters
or calculated deductions to construct expected results.

References:
- IRC 104(a)(3), 105(a): taxable disability is total less exempt benefits.
- Form 1040 line 1h and the Standard Deduction Worksheet for Dependents:
  https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf
  https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf
- Schedule SE, lines 4a, 4c and 12-13: 92.35% of business profit, the $400
  net-earnings threshold, 15.3% tax and half of that tax deductible. Drawn
  wages plus business income stay below every year's Social Security cap:
  https://www.irs.gov/pub/irs-prior/f1040sse--2024.pdf
- Publication 501 Table 2 (single dependents):
  https://www.irs.gov/pub/irs-prior/p501--2024.pdf#page=4
  https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4
- 2026 amounts: Rev. Proc. 2025-32, section 4.14:
  https://www.irs.gov/pub/irs-drop/rp-25-32.pdf#page=18
- IRC 6012(f) for 2024-2025, and 6012(a)(1) for 2026. Claimable filers
  retain the dependent worksheet in every year (decision d1395):
  https://www.law.cornell.edu/uscode/text/26/6012

The federal deduction worksheet and Medicaid Table 2 reference use W-2 box 1
wages after elective deferrals, plus earned disability and business income,
less Schedule 1 line 15 (2025 Form 1040 instructions, pp. 25 and 35).
These properties concern section 6012's income tests, not separate Schedule
SE filing duties.
"""

import numpy as np
from hypothesis import HealthCheck, given, seed, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

YEARS = (2024, 2025, 2026)
# Published single-filer amounts, independent of the model's parameter tree.
# Each tuple is (regular deduction, dependent floor, age/blindness addition).
AMOUNTS = {
    2024: (14_600, 1_300, 1_950),
    2025: (15_750, 1_350, 2_000),
    2026: (16_100, 1_350, 2_050),
}
EARNED_ADDITION = 450


def filer(**inputs):
    return {
        "age": 40,
        "is_blind": False,
        "claimed_as_dependent_on_another_return": True,
        "employment_income": 0,
        "traditional_401k_contributions": 0,
        "self_employment_income": 0,
        "taxable_interest_income": 0,
        "disability_benefits": 0,
        "tax_exempt_disability_benefits": 0,
        "disability_benefits_before_minimum_retirement_age": 0,
        **inputs,
    }


@st.composite
def filers(draw):
    wages = draw(st.integers(0, 30_000))
    return filer(
        age=draw(st.sampled_from([19, 40, 64, 65, 66, 80])),
        is_blind=draw(st.booleans()),
        claimed_as_dependent_on_another_return=draw(st.booleans()),
        employment_income=wages,
        traditional_401k_contributions=draw(st.integers(0, wages)),
        self_employment_income=draw(
            st.one_of(st.just(0), st.integers(-10_000, 30_000))
        ),
        taxable_interest_income=draw(st.integers(0, 5_000)),
        disability_benefits=draw(st.integers(0, 30_000)),
        # Overstated exemptions and negative/overstated before-retirement
        # amounts exercise both floors and the earned-income cap.
        tax_exempt_disability_benefits=draw(st.integers(0, 40_000)),
        disability_benefits_before_minimum_retirement_age=draw(
            st.integers(-5_000, 40_000)
        ),
    )


ANCHORS = [
    filer(
        disability_benefits=5_000,
        disability_benefits_before_minimum_retirement_age=5_000,
    ),
    filer(disability_benefits=5_000),
    filer(disability_benefits=5_000, tax_exempt_disability_benefits=6_000),
    filer(
        disability_benefits=5_000,
        disability_benefits_before_minimum_retirement_age=-1,
    ),
    filer(
        disability_benefits=5_000,
        tax_exempt_disability_benefits=2_000,
        disability_benefits_before_minimum_retirement_age=6_000,
    ),
    # H2: $6,000 business profit and $5,000 of earned disability.
    filer(
        self_employment_income=6_000,
        disability_benefits=7_000,
        disability_benefits_before_minimum_retirement_age=5_000,
    ),
    # Combined deferrals/disability regression in 2025: $15,000 earned and
    # gross income, with a $15,450 dependent deduction, means no return.
    filer(
        employment_income=18_000,
        traditional_401k_contributions=6_000,
        disability_benefits=3_000,
        disability_benefits_before_minimum_retirement_age=3_000,
    ),
    # Line 15 makes both filing tests true: $2,351 gross exceeds the
    # $901 + $1,000 - $63.65 + $450 = $2,287.35 dependent deduction.
    filer(
        self_employment_income=901,
        taxable_interest_income=450,
        disability_benefits=1_000,
        disability_benefits_before_minimum_retirement_age=1_000,
    ),
    filer(employment_income=2_000, self_employment_income=-5_000),
    filer(employment_income=2_000, self_employment_income=-100),
    # Schedule SE line 4a falls just below/above $400 at these profits.
    # Wages put the worksheet above its floor so line 15 affects the result.
    filer(employment_income=2_000, self_employment_income=433),
    filer(employment_income=2_000, self_employment_income=434),
    filer(
        age=65,
        is_blind=True,
        disability_benefits=5_000,
        tax_exempt_disability_benefits=500,
        disability_benefits_before_minimum_retirement_age=3_500,
    ),
    filer(
        is_blind=True,
        claimed_as_dependent_on_another_return=False,
        disability_benefits=17_000,
    ),
]
# Disability income at the statutory threshold distinguishes strict > in
# 2024-2025 from >= for unclaimable filers in 2026, and exercises the earned
# cap of the dependent worksheet at equality.
for regular, _, _ in AMOUNTS.values():
    for claimed in (False, True):
        ANCHORS.append(
            filer(
                claimed_as_dependent_on_another_return=claimed,
                disability_benefits=regular,
                disability_benefits_before_minimum_retirement_age=regular,
            )
        )


def simulate(people):
    groups = {
        entity: {}
        for entity in (
            "tax_units",
            "households",
            "marital_units",
            "spm_units",
            "families",
        )
    }
    person_inputs = {}
    for index, person in enumerate(people):
        name = f"person_{index}"
        inputs = {**person, "tax_unit_role_input": "HEAD"}
        person_inputs[name] = {
            variable: {year: value for year in YEARS}
            for variable, value in inputs.items()
        }
        for entity, units in groups.items():
            units[name] = {"members": [name]}
            if entity == "tax_units":
                units[name]["filing_status"] = {year: "SINGLE" for year in YEARS}
            elif entity == "households":
                units[name]["state_code"] = {year: "TX" for year in YEARS}
    return Simulation(
        situation={"people": person_inputs, **groups}, tax_benefit_system=SYSTEM
    )


def reference(person, year):
    """Paper-form arithmetic for a single person's section 6012 tests."""
    regular, floor, addition = AMOUNTS[year]
    taxable = max(
        0, person["disability_benefits"] - person["tax_exempt_disability_benefits"]
    )
    earned_disability = min(
        taxable, max(0, person["disability_benefits_before_minimum_retirement_age"])
    )
    wages = max(
        0, person["employment_income"] - person["traditional_401k_contributions"]
    )
    business = person["self_employment_income"]
    interest = person["taxable_interest_income"]
    gross = wages + max(0, business) + interest + taxable
    earned = wages + business + earned_disability
    unearned = interest + taxable - earned_disability
    extra_count = int(person["age"] >= 65) + int(person["is_blind"])
    extra = addition * extra_count

    # Schedule SE lines 4a, 4c, 12 and 13, below the Social Security cap.
    net_business = business * 0.9235
    line_15 = net_business * 0.153 / 2 if net_business >= 400 else 0
    worksheet_earned = max(0, earned - line_15)
    worksheet_deduction = min(regular, max(floor, worksheet_earned + EARNED_ADDITION))
    claimed = person["claimed_as_dependent_on_another_return"]
    basic = worksheet_deduction if claimed else regular
    standard = basic + extra

    # A claimed dependent keeps the section 63(c)(5) worksheet and Table 2's
    # unearned-income test. Otherwise 6012(f) includes blindness through 2025,
    # and 6012(a)(1) in 2026 permits the age addition only, with >= at equality.
    if claimed:
        required = gross > standard or unearned > floor + extra
    elif year <= 2025:
        required = gross > standard
    else:
        required = gross >= regular + addition * int(person["age"] >= 65)

    # Table 2 has three distinct tests: unearned, earned and gross income.
    # Business losses lower earned income but cannot reclassify wages or
    # disability pensions as unearned income.
    table_2_gross_limit = (
        max(floor, min(worksheet_earned, regular - EARNED_ADDITION) + EARNED_ADDITION)
        + extra
    )
    medicaid_required = (
        unearned > floor + extra
        or worksheet_earned > regular + extra
        or gross > table_2_gross_limit
    )
    return {
        "taxable_disability_benefits": taxable,
        "earned_disability_benefits": earned_disability,
        "irs_gross_income": gross,
        "basic_standard_deduction": basic,
        "standard_deduction": standard,
        "tax_unit_is_required_to_file": required,
        "medicaid_person_is_required_to_file": medicaid_required,
    }


@seed(20261007)
@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(drawn=st.lists(filers(), min_size=24, max_size=32))
def test_disability_filing_worksheet_properties(drawn):
    people = ANCHORS + drawn
    simulation = simulate(people)
    for year in YEARS:
        expected = [reference(person, year) for person in people]
        actual = {}
        for variable in expected[0]:
            actual[variable] = np.asarray(simulation.calculate(variable, year))
            values = np.asarray([row[variable] for row in expected])
            if values.dtype == bool:
                np.testing.assert_array_equal(
                    actual[variable], values, err_msg=f"{year}: {variable}"
                )
            else:
                np.testing.assert_allclose(
                    actual[variable],
                    values,
                    rtol=0,
                    atol=0.01,
                    err_msg=f"{year}: {variable}",
                )
        taxable = actual["taxable_disability_benefits"]
        earned = actual["earned_disability_benefits"]
        assert np.all((earned >= 0) & (earned <= taxable))
        for variable in (
            "tax_unit_is_required_to_file",
            "medicaid_person_is_required_to_file",
        ):
            assert actual[variable].any() and not actual[variable].all()
