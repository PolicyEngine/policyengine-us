import pytest
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2026"
WAGES = 100_000


def make_simulation(
    state_code: str,
    *,
    county: str | None = None,
    employment_income: float = WAGES,
    employer_headcount: int = 100,
    employer_quarterly_payroll_expense_override: float = -1,
) -> Simulation:
    household = {
        "members": ["person"],
        "state_code": {PERIOD: state_code},
    }
    if county is not None:
        household["county"] = {PERIOD: county}

    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employment_income": {PERIOD: employment_income},
                    "employer_headcount": {PERIOD: employer_headcount},
                    "employer_quarterly_payroll_expense_override": {
                        PERIOD: employer_quarterly_payroll_expense_override
                    },
                }
            },
            "households": {"household": household},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


def calculate(sim: Simulation, variable: str) -> float:
    return sim.calculate(variable, PERIOD)[0]


def make_employer_total_simulation(
    state_code: str,
    *,
    employer_headcount: int = 100,
    employer_state_unemployment_tax_rate_override: float = -1,
    employer_total_payroll_tax_gross_wages: float = WAGES,
    employer_total_taxable_earnings_for_social_security: float = WAGES,
    employer_total_taxable_earnings_for_federal_unemployment_tax: float = 7_000,
    employer_total_taxable_earnings_for_state_unemployment_tax: float = 9_000,
    employer_ny_mctmt_zone_1_quarterly_payroll_expense: float = 0,
    employer_ny_mctmt_zone_2_quarterly_payroll_expense: float = 0,
    employer_total_co_denver_occupational_privilege_tax_employee_months: int = 0,
    employer_total_co_denver_occupational_privilege_tax_owner_months: int = 0,
    employer_total_co_glendale_occupational_privilege_tax_employee_months: int = 0,
    employer_total_co_glendale_occupational_privilege_tax_owner_months: int = 0,
    employer_total_co_greenwood_village_occupational_privilege_tax_employee_months: int = 0,
    employer_total_co_greenwood_village_occupational_privilege_tax_owner_months: int = 0,
    employer_total_co_sheridan_occupational_privilege_tax_employee_months: int = 0,
    employer_total_mo_st_louis_payroll_expense: float = 0,
    employer_total_or_trimet_taxable_wages: float = 0,
    employer_total_or_lane_transit_district_taxable_wages: float = 0,
    employer_total_wa_seattle_social_housing_excess_compensation: float = 0,
    employer_total_wa_seattle_payroll_expense_prior_year_total: float = 0,
    employer_total_wa_seattle_payroll_expense_current_year_total: float = 0,
    employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll: float = 0,
    employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll: float = 0,
) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employer_headcount": {PERIOD: employer_headcount},
                    "employer_state_unemployment_tax_rate_override": {
                        PERIOD: employer_state_unemployment_tax_rate_override
                    },
                    "employer_total_payroll_tax_gross_wages": {
                        PERIOD: employer_total_payroll_tax_gross_wages
                    },
                    "employer_total_taxable_earnings_for_social_security": {
                        PERIOD: employer_total_taxable_earnings_for_social_security
                    },
                    "employer_total_taxable_earnings_for_federal_unemployment_tax": {
                        PERIOD: employer_total_taxable_earnings_for_federal_unemployment_tax
                    },
                    "employer_total_taxable_earnings_for_state_unemployment_tax": {
                        PERIOD: employer_total_taxable_earnings_for_state_unemployment_tax
                    },
                    "employer_ny_mctmt_zone_1_quarterly_payroll_expense": {
                        PERIOD: employer_ny_mctmt_zone_1_quarterly_payroll_expense
                    },
                    "employer_ny_mctmt_zone_2_quarterly_payroll_expense": {
                        PERIOD: employer_ny_mctmt_zone_2_quarterly_payroll_expense
                    },
                    "employer_total_co_denver_occupational_privilege_tax_employee_months": {
                        PERIOD: employer_total_co_denver_occupational_privilege_tax_employee_months
                    },
                    "employer_total_co_denver_occupational_privilege_tax_owner_months": {
                        PERIOD: employer_total_co_denver_occupational_privilege_tax_owner_months
                    },
                    "employer_total_co_glendale_occupational_privilege_tax_employee_months": {
                        PERIOD: employer_total_co_glendale_occupational_privilege_tax_employee_months
                    },
                    "employer_total_co_glendale_occupational_privilege_tax_owner_months": {
                        PERIOD: employer_total_co_glendale_occupational_privilege_tax_owner_months
                    },
                    "employer_total_co_greenwood_village_occupational_privilege_tax_employee_months": {
                        PERIOD: employer_total_co_greenwood_village_occupational_privilege_tax_employee_months
                    },
                    "employer_total_co_greenwood_village_occupational_privilege_tax_owner_months": {
                        PERIOD: employer_total_co_greenwood_village_occupational_privilege_tax_owner_months
                    },
                    "employer_total_co_sheridan_occupational_privilege_tax_employee_months": {
                        PERIOD: employer_total_co_sheridan_occupational_privilege_tax_employee_months
                    },
                    "employer_total_mo_st_louis_payroll_expense": {
                        PERIOD: employer_total_mo_st_louis_payroll_expense
                    },
                    "employer_total_or_trimet_taxable_wages": {
                        PERIOD: employer_total_or_trimet_taxable_wages
                    },
                    "employer_total_or_lane_transit_district_taxable_wages": {
                        PERIOD: employer_total_or_lane_transit_district_taxable_wages
                    },
                    "employer_total_wa_seattle_social_housing_excess_compensation": {
                        PERIOD: employer_total_wa_seattle_social_housing_excess_compensation
                    },
                    "employer_total_wa_seattle_payroll_expense_prior_year_total": {
                        PERIOD: employer_total_wa_seattle_payroll_expense_prior_year_total
                    },
                    "employer_total_wa_seattle_payroll_expense_current_year_total": {
                        PERIOD: employer_total_wa_seattle_payroll_expense_current_year_total
                    },
                    "employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll": {
                        PERIOD: employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll
                    },
                    "employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll": {
                        PERIOD: employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll
                    },
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {PERIOD: state_code},
                }
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


@pytest.mark.parametrize(
    ("state_code", "expected"),
    [
        pytest.param(
            "CA",
            {
                "ca_employee_state_disability_insurance_contribution": 1_300,
                "ca_employee_state_payroll_tax": 1_300,
                "employee_state_payroll_tax": 1_300,
            },
            id="CA",
        ),
        pytest.param(
            "CO",
            {
                "co_employee_famli_contribution": 440,
                "co_employee_state_payroll_tax": 440,
                "employee_state_payroll_tax": 440,
            },
            id="CO",
        ),
        pytest.param(
            "CT",
            {
                "ct_employee_paid_leave_contribution": 500,
                "ct_employee_state_payroll_tax": 500,
                "employee_state_payroll_tax": 500,
            },
            id="CT",
        ),
        pytest.param(
            "DE",
            {
                "de_employee_paid_leave_contribution": 400,
                "de_employee_state_payroll_tax": 400,
                "employee_state_payroll_tax": 400,
            },
            id="DE",
        ),
        pytest.param(
            "MA",
            {
                "ma_employee_paid_leave_contribution": 460,
                "ma_employee_state_payroll_tax": 460,
                "employee_state_payroll_tax": 460,
            },
            id="MA",
        ),
        pytest.param(
            "ME",
            {
                "me_employee_paid_leave_contribution": 500,
                "me_employee_state_payroll_tax": 500,
                "employee_state_payroll_tax": 500,
            },
            id="ME",
        ),
        pytest.param(
            "NJ",
            {
                "nj_employee_temporary_disability_insurance_contribution": 190,
                "nj_employee_family_leave_insurance_contribution": 230,
                "nj_employee_state_payroll_tax": 420,
                "employee_state_payroll_tax": 420,
            },
            id="NJ",
        ),
        pytest.param(
            "NY",
            {
                "ny_employee_paid_family_leave_contribution": 411.91,
                "ny_employee_disability_benefits_contribution": 31.2,
                "ny_employee_state_payroll_tax": 443.11,
                "employee_state_payroll_tax": 443.11,
            },
            id="NY",
        ),
        pytest.param(
            "OR",
            {
                "or_employee_paid_leave_contribution": 600,
                "or_employee_statewide_transit_tax": 100,
                "or_employee_state_payroll_tax": 700,
                "employee_state_payroll_tax": 700,
            },
            id="OR",
        ),
        pytest.param(
            "RI",
            {
                "ri_employee_temporary_disability_insurance_contribution": 1_100,
                "ri_employee_state_payroll_tax": 1_100,
                "employee_state_payroll_tax": 1_100,
            },
            id="RI",
        ),
        pytest.param(
            "VT",
            {
                "vt_employee_child_care_contribution": 110,
                "vt_employee_state_payroll_tax": 110,
                "employee_state_payroll_tax": 110,
            },
            id="VT",
        ),
        pytest.param(
            "WA",
            {
                "wa_employee_paid_leave_contribution": 807.159,
                "wa_employee_long_term_care_contribution": 580,
                "wa_employee_state_payroll_tax": 1_387.159,
                "employee_state_payroll_tax": 1_387.159,
            },
            id="WA",
        ),
    ],
)
def test_employee_state_payroll_contributions(
    state_code: str, expected: dict[str, float]
):
    sim = make_simulation(state_code)

    for variable, amount in expected.items():
        assert calculate(sim, variable) == pytest.approx(amount, abs=0.01)

    employee_payroll_components = sum(
        calculate(sim, variable)
        for variable in (
            "employee_social_security_tax",
            "employee_medicare_tax",
            "additional_medicare_tax",
            "employee_state_payroll_tax",
        )
    )
    assert calculate(sim, "employee_payroll_tax") == pytest.approx(
        employee_payroll_components
    )


def test_employee_payroll_tax_zero_when_payroll_tax_abolished():
    reform = Reform.from_dict(
        {
            "gov.contrib.ubi_center.flat_tax.abolish_payroll_tax": {
                "2026-01-01.2026-12-31": True,
            }
        },
        country_id="us",
    )
    sim = Simulation(
        tax_benefit_system=CountryTaxBenefitSystem(reform=(reform,)),
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employment_income": {PERIOD: WAGES},
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {PERIOD: "CA"},
                }
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert calculate(sim, "employee_payroll_tax") == 0


@pytest.mark.parametrize(
    ("state_code", "expected"),
    [
        pytest.param(
            "CA",
            {
                "ca_employer_employment_training_tax": 7,
                "ca_employer_additional_state_payroll_tax": 7,
            },
            id="CA",
        ),
        pytest.param(
            "CO",
            {
                "co_employer_famli_contribution": 440,
                "co_employer_additional_state_payroll_tax": 440,
            },
            id="CO",
        ),
        pytest.param(
            "DC",
            {
                "dc_employer_paid_leave_tax": 750,
                "dc_employer_additional_state_payroll_tax": 750,
            },
            id="DC",
        ),
        pytest.param(
            "DE",
            {
                "de_employer_paid_leave_contribution": 400,
                "de_employer_additional_state_payroll_tax": 400,
            },
            id="DE",
        ),
        pytest.param(
            "MA",
            {
                "ma_employer_paid_leave_contribution": 420,
                "ma_employer_additional_state_payroll_tax": 420,
            },
            id="MA",
        ),
        pytest.param(
            "ME",
            {
                "me_employer_paid_leave_contribution": 500,
                "me_employer_additional_state_payroll_tax": 500,
            },
            id="ME",
        ),
        pytest.param(
            "OR",
            {
                "or_employer_paid_leave_contribution": 400,
                "or_employer_additional_state_payroll_tax": 400,
            },
            id="OR",
        ),
        pytest.param(
            "RI",
            {
                "ri_employer_job_development_fund_tax": 61.32,
                "ri_employer_additional_state_payroll_tax": 61.32,
            },
            id="RI",
        ),
        pytest.param(
            "VT",
            {
                "vt_employer_child_care_contribution": 330,
                "vt_employer_additional_state_payroll_tax": 330,
            },
            id="VT",
        ),
        pytest.param(
            "WA",
            {
                "wa_employer_paid_leave_contribution": 322.841,
                "wa_employer_additional_state_payroll_tax": 322.841,
            },
            id="WA",
        ),
    ],
)
def test_employer_state_payroll_contributions(
    state_code: str, expected: dict[str, float]
):
    sim = make_simulation(state_code)

    for variable, amount in expected.items():
        assert calculate(sim, variable) == pytest.approx(amount, abs=0.01)

    employer_state_components = sum(
        calculate(sim, variable)
        for variable in (
            "employer_state_unemployment_tax",
            "employer_additional_state_payroll_tax",
        )
    )
    assert calculate(sim, "employer_state_payroll_tax") == pytest.approx(
        employer_state_components
    )

    employer_components = sum(
        calculate(sim, variable)
        for variable in (
            "employer_social_security_tax",
            "employer_medicare_tax",
            "employer_federal_unemployment_tax",
            "employer_state_payroll_tax",
            "employer_local_payroll_tax",
        )
    )
    assert calculate(sim, "employer_payroll_tax") == pytest.approx(employer_components)


@pytest.mark.parametrize(
    ("state_code", "headcount", "variable"),
    [
        pytest.param("CO", 9, "co_employer_famli_contribution", id="CO"),
        pytest.param("MA", 24, "ma_employer_paid_leave_contribution", id="MA"),
        pytest.param("ME", 14, "me_employer_paid_leave_contribution", id="ME"),
        pytest.param("OR", 24, "or_employer_paid_leave_contribution", id="OR"),
        pytest.param("WA", 49, "wa_employer_paid_leave_contribution", id="WA"),
    ],
)
def test_small_employer_thresholds_zero_employer_paid_leave_share(
    state_code: str, headcount: int, variable: str
):
    sim = make_simulation(state_code, employer_headcount=headcount)

    assert calculate(sim, variable) == 0


@pytest.mark.parametrize(
    ("headcount", "expected_rate", "expected_contribution"),
    [
        pytest.param(5, 0, 0, id="small-employer-exempt"),
        pytest.param(20, 0.0032, 160, id="medium-employer-parental-only"),
        pytest.param(30, 0.008, 400, id="full-coverage-employer"),
    ],
)
def test_delaware_paid_leave_headcount_tiers(
    headcount: int, expected_rate: float, expected_contribution: float
):
    sim = make_simulation("DE", employer_headcount=headcount, employment_income=50_000)

    assert calculate(sim, "de_paid_leave_contribution_rate") == pytest.approx(
        expected_rate
    )
    assert calculate(sim, "de_employee_paid_leave_contribution") == pytest.approx(
        expected_contribution * 0.5
    )
    assert calculate(sim, "de_employer_paid_leave_contribution") == pytest.approx(
        expected_contribution * 0.5
    )


@pytest.mark.parametrize(
    (
        "county",
        "quarterly_override",
        "headcount",
        "expected_quarterly_payroll",
        "expected_tax",
    ),
    [
        pytest.param(
            "NEW_YORK_COUNTY_NY",
            3_000_000,
            100,
            3_000_000,
            895,
            id="zone-1-override",
        ),
        pytest.param(
            "WESTCHESTER_COUNTY_NY",
            3_000_000,
            100,
            3_000_000,
            635,
            id="zone-2-override",
        ),
        pytest.param(
            "ALBANY_COUNTY_NY",
            3_000_000,
            100,
            3_000_000,
            0,
            id="outside-mctd",
        ),
        pytest.param(
            "NEW_YORK_COUNTY_NY",
            -1,
            100,
            2_500_000,
            600,
            id="zone-1-proxy",
        ),
    ],
)
def test_new_york_mctmt_employer_tax(
    county: str,
    quarterly_override: float,
    headcount: int,
    expected_quarterly_payroll: float,
    expected_tax: float,
):
    sim = make_simulation(
        "NY",
        county=county,
        employer_headcount=headcount,
        employer_quarterly_payroll_expense_override=quarterly_override,
    )

    assert calculate(
        sim, "ny_mctmt_employer_quarterly_payroll_expense"
    ) == pytest.approx(expected_quarterly_payroll)
    assert calculate(sim, "ny_mctmt_employer_tax") == pytest.approx(
        expected_tax, abs=0.01
    )
    assert calculate(sim, "employer_local_payroll_tax") == pytest.approx(
        expected_tax, abs=0.01
    )


@pytest.mark.parametrize(
    ("state_code", "headcount", "ss_taxable", "state_ui_taxable", "expected"),
    [
        pytest.param("CA", 100, WAGES, 7_000, 7, id="CA"),
        pytest.param("CO", 100, WAGES, 9_000, 440, id="CO"),
        pytest.param("DC", 100, WAGES, 9_000, 750, id="DC"),
        pytest.param("DE", 100, WAGES, 9_000, 400, id="DE"),
        pytest.param("MA", 100, WAGES, 9_000, 420, id="MA"),
        pytest.param("ME", 100, WAGES, 9_000, 500, id="ME"),
        pytest.param("OR", 100, WAGES, 9_000, 400, id="OR"),
        pytest.param("RI", 100, WAGES, 29_200, 61.32, id="RI"),
        pytest.param("VT", 100, WAGES, 9_000, 330, id="VT"),
        pytest.param("WA", 100, WAGES, 9_000, 322.841, id="WA"),
    ],
)
def test_employer_total_additional_state_payroll_tax(
    state_code: str,
    headcount: int,
    ss_taxable: float,
    state_ui_taxable: float,
    expected: float,
):
    sim = make_employer_total_simulation(
        state_code,
        employer_headcount=headcount,
        employer_total_taxable_earnings_for_social_security=ss_taxable,
        employer_total_taxable_earnings_for_state_unemployment_tax=state_ui_taxable,
    )

    assert calculate(
        sim, "employer_total_additional_state_payroll_tax"
    ) == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize(
    ("zone_1_quarterly_payroll", "zone_2_quarterly_payroll", "expected"),
    [
        pytest.param(3_000_000, 0, 107_400, id="zone-1"),
        pytest.param(0, 3_000_000, 76_200, id="zone-2"),
        pytest.param(2_500_000, 0, 60_000, id="top-threshold-exclusive"),
    ],
)
def test_ny_mctmt_total_employer_tax(
    zone_1_quarterly_payroll: float,
    zone_2_quarterly_payroll: float,
    expected: float,
):
    sim = make_employer_total_simulation(
        "NY",
        employer_total_taxable_earnings_for_state_unemployment_tax=0,
        employer_ny_mctmt_zone_1_quarterly_payroll_expense=zone_1_quarterly_payroll,
        employer_ny_mctmt_zone_2_quarterly_payroll_expense=zone_2_quarterly_payroll,
    )

    assert calculate(sim, "ny_mctmt_total_employer_tax") == pytest.approx(
        expected, abs=0.01
    )
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(
        expected, abs=0.01
    )


def test_colorado_total_business_occupational_privilege_taxes():
    sim = make_employer_total_simulation(
        "CO",
        employer_total_co_denver_occupational_privilege_tax_employee_months=12,
        employer_total_co_denver_occupational_privilege_tax_owner_months=6,
        employer_total_co_glendale_occupational_privilege_tax_employee_months=12,
        employer_total_co_glendale_occupational_privilege_tax_owner_months=12,
        employer_total_co_greenwood_village_occupational_privilege_tax_employee_months=12,
        employer_total_co_greenwood_village_occupational_privilege_tax_owner_months=6,
        employer_total_co_sheridan_occupational_privilege_tax_employee_months=12,
    )

    assert calculate(
        sim, "co_denver_total_business_occupational_privilege_tax"
    ) == pytest.approx(72)
    assert calculate(
        sim, "co_glendale_total_business_occupational_privilege_tax"
    ) == pytest.approx(120)
    assert calculate(
        sim, "co_greenwood_village_total_business_occupational_privilege_tax"
    ) == pytest.approx(36)
    assert calculate(
        sim, "co_sheridan_total_business_occupational_privilege_tax"
    ) == pytest.approx(36)
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(264)


def test_oregon_total_local_payroll_taxes():
    sim = make_employer_total_simulation(
        "OR",
        employer_total_or_trimet_taxable_wages=1_000_000,
        employer_total_or_lane_transit_district_taxable_wages=1_000_000,
    )

    assert calculate(sim, "or_trimet_total_payroll_tax") == pytest.approx(8_237)
    assert calculate(
        sim, "or_lane_transit_district_total_payroll_tax"
    ) == pytest.approx(8_000)
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(16_237)


@pytest.mark.parametrize(
    (
        "prior_year_total",
        "current_year_total",
        "lower_band_taxable_payroll",
        "upper_band_taxable_payroll",
        "expected",
    ),
    [
        pytest.param(
            9_000_000,
            20_000_000,
            1_000_000,
            500_000,
            0,
            id="below-subject-threshold",
        ),
        pytest.param(
            10_000_000,
            20_000_000,
            1_000_000,
            500_000,
            16_515,
            id="lower-schedule",
        ),
        pytest.param(
            10_000_000,
            200_000_000,
            1_000_000,
            500_000,
            17_580,
            id="middle-schedule",
        ),
        pytest.param(
            10_000_000,
            2_000_000_000,
            1_000_000,
            500_000,
            27_705,
            id="top-schedule",
        ),
    ],
)
def test_seattle_total_payroll_expense_tax(
    prior_year_total: float,
    current_year_total: float,
    lower_band_taxable_payroll: float,
    upper_band_taxable_payroll: float,
    expected: float,
):
    sim = make_employer_total_simulation(
        "WA",
        employer_total_wa_seattle_payroll_expense_prior_year_total=prior_year_total,
        employer_total_wa_seattle_payroll_expense_current_year_total=current_year_total,
        employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll=lower_band_taxable_payroll,
        employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll=upper_band_taxable_payroll,
    )

    assert calculate(sim, "wa_seattle_total_payroll_expense_tax") == pytest.approx(
        expected
    )
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(expected)


def test_st_louis_total_payroll_expense_tax():
    sim = make_employer_total_simulation(
        "MO", employer_total_mo_st_louis_payroll_expense=1_000_000
    )

    assert calculate(sim, "mo_st_louis_total_payroll_expense_tax") == pytest.approx(
        5_000
    )
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(5_000)
    assert calculate(sim, "employer_total_payroll_tax") == pytest.approx(12_906.2)
    assert calculate(sim, "employer_total_cost_of_employment") == pytest.approx(
        112_906.2
    )


def test_seattle_total_social_housing_tax():
    sim = make_employer_total_simulation(
        "WA",
        employer_total_wa_seattle_payroll_expense_prior_year_total=10_000_000,
        employer_total_wa_seattle_payroll_expense_current_year_total=20_000_000,
        employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll=1_000_000,
        employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll=500_000,
        employer_total_wa_seattle_social_housing_excess_compensation=500_000,
    )

    assert calculate(sim, "wa_seattle_total_social_housing_tax") == pytest.approx(
        25_000
    )
    assert calculate(sim, "employer_total_local_payroll_tax") == pytest.approx(41_515)


def test_employer_total_payroll_tax_aggregates_employer_inputs():
    sim = make_employer_total_simulation("TX")

    assert calculate(sim, "employer_total_social_security_tax") == pytest.approx(6_200)
    assert calculate(sim, "employer_total_medicare_tax") == pytest.approx(1_450)
    assert calculate(sim, "employer_total_federal_unemployment_tax") == pytest.approx(
        42
    )
    assert calculate(sim, "employer_total_state_unemployment_tax") == pytest.approx(243)
    assert calculate(sim, "employer_total_state_payroll_tax") == pytest.approx(243)
    assert calculate(sim, "employer_total_payroll_tax") == pytest.approx(7_935)
    assert calculate(sim, "employer_total_cost_of_employment") == pytest.approx(107_935)


def test_employee_state_payroll_tax_flows_into_household_net_income():
    wa_sim = make_simulation("WA")
    tx_sim = make_simulation("TX")

    wa_state_payroll_tax = calculate(wa_sim, "employee_state_payroll_tax")
    household_tax_difference = calculate(
        wa_sim, "household_tax_before_refundable_credits"
    ) - calculate(tx_sim, "household_tax_before_refundable_credits")
    household_net_income_difference = calculate(
        tx_sim, "household_net_income"
    ) - calculate(wa_sim, "household_net_income")

    assert household_tax_difference == pytest.approx(wa_state_payroll_tax, abs=0.01)
    assert household_net_income_difference == pytest.approx(
        wa_state_payroll_tax, abs=0.01
    )
