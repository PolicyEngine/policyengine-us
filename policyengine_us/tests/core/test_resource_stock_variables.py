from policyengine_us import CountryTaxBenefitSystem, Simulation


RESOURCE_STOCK_VARIABLES = [
    "ca_capi_resources",
    "ca_tanf_resources",
    "ca_tanf_resources_limit",
    "dc_tanf_countable_resources",
    "in_tanf_countable_resources",
    "la_general_relief_cash_asset_limit",
    "mt_tanf_countable_resources",
    "nm_works_countable_liquid_resources",
    "nm_works_countable_non_liquid_resources",
    "nm_works_countable_resources",
    "ssi_countable_resources",
    "tn_ff_countable_resources",
    "tx_tanf_countable_resources",
    "wa_tanf_countable_resources",
    "wi_works_countable_resources",
]

SSI_MONTHLY_VARIABLES = [
    "is_ssi_eligible",
    "meets_ssi_resource_test",
    "ssi",
    "ssi_amount_if_eligible",
    "uncapped_ssi",
]


def test_resource_variables_are_stocks():
    system = CountryTaxBenefitSystem()

    non_stock_variables = [
        variable
        for variable in RESOURCE_STOCK_VARIABLES
        if system.variables[variable].quantity_type != "stock"
    ]

    assert non_stock_variables == []


def test_ssi_payment_and_eligibility_variables_are_monthly():
    system = CountryTaxBenefitSystem()

    non_monthly_variables = [
        variable
        for variable in SSI_MONTHLY_VARIABLES
        if system.variables[variable].definition_period != "month"
    ]

    assert non_monthly_variables == []


def test_annual_resource_aggregate_is_not_divided_in_monthly_period():
    situation = {
        "people": {
            "person1": {
                "age": {"2026": 70},
                "bank_account_assets": {"2026": 2_100},
            }
        },
        "families": {"family": {"members": ["person1"]}},
        "marital_units": {"marital_unit": {"members": ["person1"]}},
        "tax_units": {"tax_unit": {"members": ["person1"]}},
        "spm_units": {"spm_unit": {"members": ["person1"]}},
        "households": {
            "household": {
                "members": ["person1"],
                "state_code": {"2026": "CA"},
            }
        },
    }
    simulation = Simulation(situation=situation)

    yearly_resources = simulation.calculate("ssi_countable_resources", "2026")
    monthly_resources = simulation.calculate("ssi_countable_resources", "2026-01")

    assert yearly_resources.tolist() == [2_100]
    assert monthly_resources.tolist() == [2_100]


def test_monthly_resource_aggregate_is_not_summed_in_annual_period():
    situation = {
        "people": {"person1": {"age": {"2026": 30}}},
        "families": {"family": {"members": ["person1"]}},
        "marital_units": {"marital_unit": {"members": ["person1"]}},
        "tax_units": {"tax_unit": {"members": ["person1"]}},
        "spm_units": {
            "spm_unit": {
                "members": ["person1"],
                "spm_unit_cash_assets": {"2026": 6_000},
            }
        },
        "households": {
            "household": {
                "members": ["person1"],
                "state_code": {"2026": "TX"},
                "household_vehicles_value": {"2026": 0},
            }
        },
    }
    simulation = Simulation(situation=situation)

    yearly_resources = simulation.calculate("tx_tanf_countable_resources", "2026")
    monthly_resources = simulation.calculate("tx_tanf_countable_resources", "2026-01")

    assert yearly_resources.tolist() == [6_000]
    assert monthly_resources.tolist() == [6_000]
