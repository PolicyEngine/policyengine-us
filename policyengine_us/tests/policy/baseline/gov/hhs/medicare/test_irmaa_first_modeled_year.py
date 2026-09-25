"""Medicare IRMAA's two-year income lag must stay within the modeled years.

Issue #9613: a 2015 or 2016 household with a member aged 65 or older raised
ParameterNotFoundError because the IRMAA MAGI read 2013 or 2014 income, before
the first year the parameters are backdated to.
"""

import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

SYSTEM = CountryTaxBenefitSystem()

FILING_STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD"]
INCOMES = [0, 30_000, 150_000, 500_000]
# Benefit years whose income year two years prior precedes the model.
UNMODELED_LAG_YEARS = [FIRST_MODELED_YEAR, FIRST_MODELED_YEAR + 1]
MODELED_LAG_YEARS = list(range(FIRST_MODELED_YEAR + 2, 2027))


def senior_household(
    year, employment_income, state_code="TX", person_inputs=None, tax_unit_inputs=None
):
    person = {"age": {year: 66}, "employment_income": {year: employment_income}}
    person.update(person_inputs or {})
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {"person": person},
            "tax_units": {
                "tax_unit": {"members": ["person"], **(tax_unit_inputs or {})}
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {year: state_code},
                }
            },
        },
    )


def cached_periods_before_first_modeled_year(simulation):
    early = []
    for population in simulation.populations.values():
        for name, holder in population._holders.items():
            for period in holder.get_known_periods():
                if period.unit != "eternity" and period.start.year < FIRST_MODELED_YEAR:
                    early.append((name, str(period)))
    return early


def test_first_modeled_year_is_the_backdating_floor():
    # The constant must match how far CountryTaxBenefitSystem backdates: a
    # parameter first dated after the floor is defined from it, not before.
    limit = SYSTEM.parameters.gov.irs.gross_income.retirement_contributions.limit
    assert limit.children["401k"](f"{FIRST_MODELED_YEAR}-01-01") > 0
    assert limit.children["401k"](f"{FIRST_MODELED_YEAR - 1}-12-31") is None


@pytest.mark.parametrize("year", UNMODELED_LAG_YEARS)
@pytest.mark.parametrize("filing_status", FILING_STATUSES)
@pytest.mark.parametrize("employment_income", INCOMES)
def test_magi_is_zero_when_lag_precedes_the_model(
    year, filing_status, employment_income
):
    sim = senior_household(
        year,
        employment_income,
        person_inputs={
            "is_medicare_eligible": {year: True},
            "medicare_enrolled": {year: True},
        },
        tax_unit_inputs={"filing_status": {year: filing_status}},
    )
    assert sim.calculate("medicare_irmaa_magi_two_years_prior", year)[0] == 0
    # With a zero MAGI, no IRMAA is added to the base Part B premium and no
    # Part D surcharge applies.
    gross = sim.calculate("gross_medicare_part_b_premium", year)[0]
    base = sim.calculate("base_part_b_premium", year)[0]
    assert gross == pytest.approx(base)
    assert sim.calculate("income_adjusted_part_d_premium_surcharge", year)[0] == 0


@pytest.mark.parametrize("year", MODELED_LAG_YEARS)
def test_magi_reads_income_two_years_prior_within_the_model(year):
    lag_year = year - 2
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {year: 66},
                    "tax_exempt_interest_income": {lag_year: 4_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "adjusted_gross_income": {lag_year: 123_000},
                }
            },
            "households": {"household": {"members": ["person"]}},
        },
    )
    assert sim.calculate("medicare_irmaa_magi_two_years_prior", year)[
        0
    ] == pytest.approx(127_000)


@pytest.mark.parametrize("year", UNMODELED_LAG_YEARS)
def test_provided_magi_still_overrides(year):
    sim = senior_household(
        year,
        30_000,
        person_inputs={"is_medicare_eligible": {year: True}},
    )
    sim.set_input("medicare_irmaa_magi_two_years_prior", year, [500_000])
    gross = sim.calculate("gross_medicare_part_b_premium", year)[0]
    base = sim.calculate("base_part_b_premium", year)[0]
    assert gross > base


@pytest.mark.parametrize("year", UNMODELED_LAG_YEARS)
@pytest.mark.parametrize("employment_income", INCOMES)
def test_senior_household_computes_without_reading_unmodeled_years(
    year, employment_income
):
    sim = senior_household(year, employment_income)
    for variable in ["income_tax", "household_net_income"]:
        sim.calculate(variable, year)
    # Nothing is computed or cached for a year before the model begins. A
    # value cached there would also be uprated from an undefined parameter
    # when a later year reads it.
    assert cached_periods_before_first_modeled_year(sim) == []
