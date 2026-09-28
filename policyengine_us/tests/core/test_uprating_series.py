"""Each dollar input follows the series closest to what it measures: its own
national series, the income source it is part of, prices for consumption
expenses and debts, CMS per-capita spending for health costs."""

from pathlib import Path

import pytest
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.data.economic_assumptions import MICRODATA_UPRATING_OVERRIDES
from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import DERIVED_FROM, per_capita_path

EMPLOYMENT = per_capita_path("calibration.gov.irs.soi.employment_income")
SELF_EMPLOYMENT = per_capita_path("calibration.gov.irs.soi.self_employment_income")
CAPITAL_GAINS = per_capita_path("calibration.gov.irs.soi.long_term_capital_gains")
ALIMONY = per_capita_path("calibration.gov.irs.soi.alimony_income")
UNEMPLOYMENT = per_capita_path("calibration.gov.irs.soi.unemployment_compensation")
DEFAULT = per_capita_path("calibration.gov.cbo.income_by_source.adjusted_gross_income")
CMS = "calibration.gov.hhs.cms.moop_per_capita"
CPI_U = "gov.bls.cpi.cpi_u"
COLA = "gov.ssa.uprating"

EXPECTED = {
    # Pay, and amounts set as a share of pay.
    "hourly_wage": EMPLOYMENT,
    "tip_income": EMPLOYMENT,
    "fsla_overtime_premium": EMPLOYMENT,
    "w2_wages_from_qualified_business": EMPLOYMENT,
    "sstb_w2_wages_from_qualified_business": EMPLOYMENT,
    "traditional_401k_contributions_desired": EMPLOYMENT,
    "roth_401k_contributions_desired": EMPLOYMENT,
    "traditional_403b_contributions_desired": EMPLOYMENT,
    "roth_403b_contributions_desired": EMPLOYMENT,
    "traditional_ira_contributions_desired": EMPLOYMENT,
    "roth_ira_contributions_desired": EMPLOYMENT,
    "military_basic_pay": EMPLOYMENT,
    "military_service_income": EMPLOYMENT,
    "state_or_federal_salary": EMPLOYMENT,
    # Wage-replacement benefits.
    "workers_compensation": EMPLOYMENT,
    "disability_benefits": EMPLOYMENT,
    "self_employed_pension_contributions_desired": SELF_EMPLOYMENT,
    # Components of capital gains.
    "long_term_capital_gains_on_collectibles": CAPITAL_GAINS,
    "unrecaptured_section_1250_gain": CAPITAL_GAINS,
    "non_sch_d_capital_gains": CAPITAL_GAINS,
    "schedule_d_capital_gain_distributions": CAPITAL_GAINS,
    "long_term_capital_gains_on_small_business_stock": CAPITAL_GAINS,
    "long_term_capital_gains_on_assets_eligible_for_vt_exclusion": CAPITAL_GAINS,
    "property_sales_net_capital_gain": CAPITAL_GAINS,
    "other_net_gain": CAPITAL_GAINS,
    # Own national series.
    "alimony_income": ALIMONY,
    "alimony_expense": ALIMONY,
    "unemployment_compensation": UNEMPLOYMENT,
    # Health costs.
    "health_insurance_premiums": CMS,
    # Benefits adjusted by the Social Security cost-of-living index.
    "veterans_benefits": COLA,
    # Consumption expenses, and the interest on debts, follow prices. The
    # structured first and second mortgage inputs stay on the default: two are
    # deprecated (issue #9275) and the file's formulas are outside the
    # selective coverage job.
    "pre_subsidy_rent": CPI_U,
    "pre_subsidy_care_expenses": CPI_U,
    "spm_unit_pre_subsidy_childcare_expenses": CPI_U,
    "after_school_expenses": CPI_U,
    "care_and_support_costs": CPI_U,
    "qualified_tuition_expenses": CPI_U,
    "tuition_and_fees": CPI_U,
    "k12_tuition_and_fees": CPI_U,
    "pre_subsidy_electricity_expense": CPI_U,
    "gas_expense": CPI_U,
    "metered_gas_expense": CPI_U,
    "bottled_gas_expense": CPI_U,
    "fuel_oil_expense": CPI_U,
    "coal_expense": CPI_U,
    "wood_expense": CPI_U,
    "other_heating_fuel_expense": CPI_U,
    "cooking_fuel_expense": CPI_U,
    "heating_cooling_expense": CPI_U,
    "heating_expense_person": CPI_U,
    "water_expense": CPI_U,
    "sewage_expense": CPI_U,
    "trash_expense": CPI_U,
    "phone_cost": CPI_U,
    "broadband_cost": CPI_U,
    "homeowners_insurance": CPI_U,
    "homeowners_association_fees": CPI_U,
    "pre_subsidy_transportation_expense": CPI_U,
    "home_mortgage_interest": CPI_U,
    "student_loan_interest": CPI_U,
    "investment_interest_expense": CPI_U,
    # Still on the default.
    "charitable_cash_donations": DEFAULT,
    "miscellaneous_income": DEFAULT,
}


def _value(path, year):
    return get_parameter(system.parameters, path)(f"{year}-01-01")


@pytest.mark.parametrize("variable, series", sorted(EXPECTED.items()))
def test_variable_follows_expected_series(variable, series):
    assert system.variables[variable].uprating == series


@pytest.mark.parametrize("series", sorted(set(EXPECTED.values())))
def test_series_is_defined_across_the_projection_window(series):
    for year in (2024, 2025, 2030, 2035):
        assert _value(series, year) not in (None, 0)


@pytest.mark.parametrize("year", (2025, 2030, 2035, 2036))
def test_unemployment_compensation_grows_with_cbo_unemployment_outlays(year):
    soi = "calibration.gov.irs.soi.unemployment_compensation"
    cbo = "calibration.gov.cbo.unemployment_compensation"
    assert _value(soi, year) / _value(soi, 2024) == pytest.approx(
        _value(cbo, year) / _value(cbo, 2024), rel=1e-12
    )


def test_unemployment_compensation_series_do_not_flatten_after_2036():
    for path in (
        "calibration.gov.cbo.unemployment_compensation",
        "calibration.gov.irs.soi.unemployment_compensation",
    ):
        assert _value(path, 2100) > _value(path, 2037) > _value(path, 2036)


def test_alimony_series_is_labelled_as_alimony():
    parameter = get_parameter(
        system.parameters, "calibration.gov.irs.soi.alimony_income"
    )
    assert parameter.metadata["label"] == "SOI alimony income"


def test_rent_override_matches_the_rent_input():
    assert MICRODATA_UPRATING_OVERRIDES["rent"] == CPI_U
    assert system.variables["pre_subsidy_rent"].uprating == CPI_U


METHODOLOGY_PAGE = (
    Path(__file__).parents[3] / "docs-quarto" / "methodology" / "spm-poverty.qmd"
)
PARAMETERS_FOLDER = "policyengine_us/parameters/"


def _authored_series(uprating):
    """The authored parameter behind an uprating path: a derived per-capita
    series names the national total it divides."""
    parameter = get_parameter(system.parameters, uprating)
    return parameter.metadata.get(DERIVED_FROM, uprating)


def _series_that_inputs_follow():
    return sorted(
        {
            _authored_series(variable.uprating)
            for variable in system.variables.values()
            if getattr(variable, "uprating", None)
        }
    )


@pytest.mark.parametrize("series", _series_that_inputs_follow())
def test_methodology_page_links_every_series_an_input_follows(series):
    """The SPM methodology page names the series each family of inputs follows
    and sends every other uprated input to the default. That stays true only
    while the page links every series some input follows: the parameter's own
    file, the file that holds it, or the folder that holds it."""
    if not METHODOLOGY_PAGE.exists():
        pytest.skip("The documentation is not part of an installed package.")
    page = METHODOLOGY_PAGE.read_text()
    path = series.replace(".", "/")
    holder = path.rpartition("/")[0]
    links = (
        f"{PARAMETERS_FOLDER}{path}.yaml",
        f"{PARAMETERS_FOLDER}{holder}.yaml",
        f"{PARAMETERS_FOLDER}{holder})",
    )
    assert any(link in page for link in links), (
        f"{METHODOLOGY_PAGE.name} does not link {series}, which uprates at "
        "least one input. Say on the page which inputs follow it."
    )
