import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2026"
WAGES = 100_000


def make_local_tax_simulation(
    state_code: str,
    *,
    pa_philadelphia_wage_tax_taxable_wages: float = 0,
    pa_philadelphia_wage_tax_resident: bool = False,
    pa_philadelphia_wage_tax_reduced_rate_eligible: bool = False,
    mo_kansas_city_earnings_tax_taxable_earnings: float = 0,
    mo_st_louis_earnings_tax_taxable_earnings: float = 0,
    mo_st_louis_earnings_tax_credit: float = 0,
    co_denver_employee_occupational_privilege_tax_months: int = 0,
    co_glendale_employee_occupational_privilege_tax_months: int = 0,
    co_greenwood_village_employee_occupational_privilege_tax_months: int = 0,
    co_sheridan_employee_occupational_privilege_tax_months: int = 0,
) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employment_income": {PERIOD: WAGES},
                    "pa_philadelphia_wage_tax_taxable_wages": {
                        PERIOD: pa_philadelphia_wage_tax_taxable_wages
                    },
                    "pa_philadelphia_wage_tax_resident": {
                        PERIOD: pa_philadelphia_wage_tax_resident
                    },
                    "pa_philadelphia_wage_tax_reduced_rate_eligible": {
                        PERIOD: pa_philadelphia_wage_tax_reduced_rate_eligible
                    },
                    "mo_kansas_city_earnings_tax_taxable_earnings": {
                        PERIOD: mo_kansas_city_earnings_tax_taxable_earnings
                    },
                    "mo_st_louis_earnings_tax_taxable_earnings": {
                        PERIOD: mo_st_louis_earnings_tax_taxable_earnings
                    },
                    "mo_st_louis_earnings_tax_credit": {
                        PERIOD: mo_st_louis_earnings_tax_credit
                    },
                    "co_denver_employee_occupational_privilege_tax_months": {
                        PERIOD: co_denver_employee_occupational_privilege_tax_months
                    },
                    "co_glendale_employee_occupational_privilege_tax_months": {
                        PERIOD: co_glendale_employee_occupational_privilege_tax_months
                    },
                    "co_greenwood_village_employee_occupational_privilege_tax_months": {
                        PERIOD: co_greenwood_village_employee_occupational_privilege_tax_months
                    },
                    "co_sheridan_employee_occupational_privilege_tax_months": {
                        PERIOD: co_sheridan_employee_occupational_privilege_tax_months
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


def calculate(sim: Simulation, variable: str) -> float:
    return sim.calculate(variable, PERIOD)[0]


@pytest.mark.parametrize(
    ("label", "state_code", "inputs", "variable", "expected"),
    [
        (
            "philadelphia_resident",
            "PA",
            {
                "pa_philadelphia_wage_tax_taxable_wages": WAGES,
                "pa_philadelphia_wage_tax_resident": True,
            },
            "pa_philadelphia_wage_tax",
            3_740,
        ),
        (
            "philadelphia_nonresident",
            "NJ",
            {
                "pa_philadelphia_wage_tax_taxable_wages": WAGES,
            },
            "pa_philadelphia_wage_tax",
            3_430,
        ),
        (
            "philadelphia_reduced_rate",
            "NJ",
            {
                "pa_philadelphia_wage_tax_taxable_wages": WAGES,
                "pa_philadelphia_wage_tax_reduced_rate_eligible": True,
            },
            "pa_philadelphia_wage_tax",
            1_500,
        ),
        (
            "kansas_city_nonresident_worker",
            "KS",
            {
                "mo_kansas_city_earnings_tax_taxable_earnings": WAGES,
            },
            "mo_kansas_city_earnings_tax",
            1_000,
        ),
        (
            "st_louis_credit",
            "IL",
            {
                "mo_st_louis_earnings_tax_taxable_earnings": WAGES,
                "mo_st_louis_earnings_tax_credit": 200,
            },
            "mo_st_louis_earnings_tax",
            800,
        ),
        (
            "st_louis_credit_floor",
            "IL",
            {
                "mo_st_louis_earnings_tax_taxable_earnings": WAGES,
                "mo_st_louis_earnings_tax_credit": 2_000,
            },
            "mo_st_louis_earnings_tax",
            0,
        ),
    ],
    ids=lambda item: item if isinstance(item, str) else None,
)
def test_local_income_tax_components(
    label: str,
    state_code: str,
    inputs: dict[str, float | bool],
    variable: str,
    expected: float,
):
    sim = make_local_tax_simulation(state_code, **inputs)
    assert calculate(sim, variable) == pytest.approx(expected, abs=0.01)


def test_local_occupational_tax_components():
    sim = make_local_tax_simulation(
        "WY",
        co_denver_employee_occupational_privilege_tax_months=12,
        co_glendale_employee_occupational_privilege_tax_months=12,
        co_greenwood_village_employee_occupational_privilege_tax_months=12,
        co_sheridan_employee_occupational_privilege_tax_months=12,
    )

    assert calculate(sim, "co_denver_employee_occupational_privilege_tax") == 69
    assert calculate(sim, "co_glendale_employee_occupational_privilege_tax") == 60
    assert (
        calculate(sim, "co_greenwood_village_employee_occupational_privilege_tax") == 24
    )
    assert calculate(sim, "co_sheridan_employee_occupational_privilege_tax") == 36
    assert calculate(sim, "local_occupational_tax") == 189


def test_local_taxes_feed_household_net_income():
    baseline = make_local_tax_simulation("PA")
    reformed = make_local_tax_simulation(
        "PA",
        pa_philadelphia_wage_tax_taxable_wages=WAGES,
        pa_philadelphia_wage_tax_resident=True,
        co_denver_employee_occupational_privilege_tax_months=12,
    )

    local_income_tax = calculate(reformed, "local_income_tax")
    local_occupational_tax = calculate(reformed, "local_occupational_tax")
    total_local_tax = local_income_tax + local_occupational_tax

    assert local_income_tax == pytest.approx(3_740, abs=0.01)
    assert local_occupational_tax == pytest.approx(69, abs=0.01)
    assert calculate(reformed, "household_tax_before_refundable_credits") - calculate(
        baseline, "household_tax_before_refundable_credits"
    ) == pytest.approx(total_local_tax, abs=0.01)
    assert calculate(baseline, "household_net_income") - calculate(
        reformed, "household_net_income"
    ) == pytest.approx(total_local_tax, abs=0.01)
