"""Property tests for two federal rules on a separate return and on wages.

1. IRC 63(c)(6)(A): a married individual filing separately whose spouse
   itemizes has a standard deduction of zero. The standard deduction is the
   sum in 63(c)(1), so this holds whatever the filer's age or blindness.
2. IRC 129(a)(1), 3121(a)(18), 3306(b)(13): employer dependent care benefits
   (W-2 box 10, Form 2441 line 12) are left out of income tax wages and of
   FICA and FUTA wages. The part above the filer's IRC 129 exclusion returns
   to gross income (Form 2441 line 26, Form 1040 line 1e). So for one earner:
     income tax wages + taxable benefits + exclusion = employment income,
     FICA wages = employment income - benefits,
     exclusion <= employment income - benefits (IRC 129(b), Form 2441
     line 18 earned income leaves out line 12 benefits).

Each example builds one simulation holding many tax units.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = [2018, 2021, 2024, 2025, 2026]
FILING_STATUSES = ["SINGLE", "SEPARATE", "HEAD_OF_HOUSEHOLD", "JOINT"]

FILER = st.fixed_dictionaries(
    {
        "age": st.integers(min_value=18, max_value=90),
        "blind": st.booleans(),
        "wages": st.integers(min_value=0, max_value=200_000),
    }
)

EARNER = st.fixed_dictionaries(
    {
        "wages": st.integers(min_value=0, max_value=150_000),
        "benefit_share": st.floats(min_value=0, max_value=1),
        "benefit_cap": st.integers(min_value=0, max_value=10_500),
        "status": st.sampled_from(FILING_STATUSES[:3]),
    }
)


def _simulate(year, people, tax_units):
    households = {
        f"h_{name}": {"members": unit["members"], "state_code": {year: "TX"}}
        for name, unit in tax_units.items()
    }
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    year=st.sampled_from(YEARS),
    filers=st.lists(FILER, min_size=1, max_size=12),
)
def test_separate_filer_whose_spouse_itemizes_has_no_standard_deduction(year, filers):
    people, tax_units = {}, {}
    for i, filer in enumerate(filers):
        people[f"p{i}"] = {
            "age": {year: filer["age"]},
            "is_blind": {year: filer["blind"]},
            "employment_income": {year: filer["wages"]},
        }
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            "filing_status": {year: "SEPARATE"},
            "separate_filer_itemizes": {year: True},
        }
    sim = _simulate(year, people, tax_units)
    assert (sim.calculate("standard_deduction", year) == 0).all()
    # The deduction a non-itemizer takes is therefore zero too.
    itemizes = sim.calculate("tax_unit_itemizes", year)
    deductions = sim.calculate("taxable_income_deductions", year)
    assert (deductions[~itemizes] == 0).all()


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    year=st.sampled_from(YEARS),
    earners=st.lists(EARNER, min_size=1, max_size=12),
)
def test_dependent_care_benefits_leave_wages_once(year, earners):
    people, tax_units, benefits = {}, {}, []
    for i, earner in enumerate(earners):
        benefit = min(
            round(earner["wages"] * earner["benefit_share"]),
            earner["benefit_cap"],
        )
        benefits.append(benefit)
        people[f"p{i}"] = {
            "age": {year: 35},
            "employment_income": {year: earner["wages"]},
            "dependent_care_employer_benefits": {year: benefit},
        }
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            "filing_status": {year: earner["status"]},
        }
    sim = _simulate(year, people, tax_units)
    wages = sim.calculate("employment_income", year)
    box_1 = sim.calculate("irs_employment_income", year)
    taxable = sim.calculate("taxable_dependent_care_benefits", year)
    exclusion = sim.calculate("dependent_care_assistance_exclusion", year)
    fica_wages = sim.calculate("payroll_tax_gross_wages", year)
    for i, benefit in enumerate(benefits):
        assert box_1[i] == wages[i] - benefit
        assert fica_wages[i] == wages[i] - benefit
        assert 0 <= taxable[i] <= benefit
        assert abs(box_1[i] + taxable[i] + exclusion[i] - wages[i]) < 0.01
        # IRC 129(b) and Form 2441 line 18: the exclusion cannot exceed
        # earned income, which leaves out the line 12 benefits. The identity
        # above holds for any exclusion, so this pins the limit itself.
        assert exclusion[i] <= max(wages[i] - benefit, 0) + 0.01
        # The exclusion reaches the smallest cap drawn ($2,500 on a separate
        # return) unless the benefits or net wages are smaller.
        assert exclusion[i] >= min(benefit, 2_500, max(wages[i] - benefit, 0)) - 0.01
