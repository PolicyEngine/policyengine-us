"""The childless EITC age test compares completed years.

IRC 32(c)(1)(A)(ii)(II) requires a filer without a qualifying child (or
either spouse) to have "attained age 25 but not attained age 65 before the
close of the taxable year". gov.irs.credits.eitc.eligibility.age.max holds
the highest completed age that qualifies, so for any age a:

1. The age test holds exactly when min <= a and floor(a) <= max, where min
   is the non-student minimum (no filer here is a student).
2. It is monotone above the minimum: once raising age fails the test, a
   higher age never passes it again.

Each example builds one simulation of single childless filers who are not
dependents, so eitc_demographic_eligible is the age test alone.
"""

import math

from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation

SYSTEM = CountryTaxBenefitSystem()
YEARS = [2018, 2020, 2021, 2022, 2024, 2025, 2026]
AGES = st.floats(min_value=25, max_value=80, allow_nan=False).map(lambda a: round(a, 2))


def _eligible(year, ages):
    people, tax_units, households = {}, {}, {}
    for i, age in enumerate(ages):
        people[f"p{i}"] = {
            "age": {year: age},
            "is_full_time_student": {year: False},
        }
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            "filing_status": {year: "SINGLE"},
        }
        households[f"h{i}"] = {"members": [f"p{i}"], "state_code": {year: "TX"}}
    sim = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )
    return sim.calculate("eitc_demographic_eligible", year)


SETTINGS = settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@SETTINGS
@given(year=st.sampled_from(YEARS), ages=st.lists(AGES, min_size=1, max_size=20))
@example(year=2024, ages=[63.99, 64.0, 64.5, 64.99, 65.0, 65.5])
@example(year=2021, ages=[64.5, 65.0, 80.0])
def test_age_test_equals_completed_years_comparison(year, ages):
    p = SYSTEM.parameters.gov.irs.credits.eitc.eligibility.age
    instant = f"{year}-01-01"
    min_age, max_age = p.min(instant), p.max(instant)
    eligible = _eligible(year, ages)
    for age, result in zip(ages, eligible):
        assert bool(result) == (min_age <= age and math.floor(age) <= max_age)


@SETTINGS
@given(year=st.sampled_from(YEARS), ages=st.lists(AGES, min_size=2, max_size=20))
@example(year=2024, ages=[64.0, 64.5, 65.0, 66.0])
def test_age_test_is_monotone_past_the_ceiling(year, ages):
    ages = sorted(ages)
    eligible = _eligible(year, ages)
    failed = False
    for result in eligible:
        if failed:
            assert not result
        failed = failed or not result
