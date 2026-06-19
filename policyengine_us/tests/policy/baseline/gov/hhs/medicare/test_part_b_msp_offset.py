import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2025"


def make_simulation(
    *,
    medicare_enrolled: bool,
    gross_part_b_premium: float,
    base_part_b_premium: float,
    msp_income_eligible: bool,
    msp_asset_eligible: bool,
) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "is_medicare_eligible": {PERIOD: True},
                    "medicare_enrolled": {PERIOD: medicare_enrolled},
                    "medicare_quarters_of_coverage": {PERIOD: 40},
                    "gross_medicare_part_b_premium": {PERIOD: gross_part_b_premium},
                    "base_part_b_premium": {PERIOD: base_part_b_premium},
                    "msp_income_eligible": {f"{PERIOD}-01": msp_income_eligible},
                    "msp_asset_eligible": {f"{PERIOD}-01": msp_asset_eligible},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


def test_msp_part_b_premium_coverage_pays_standard_premium():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=4_440,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(
        2_220
    )


def test_medicare_part_b_premium_preserves_only_irmaa_above_msp_support():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=4_440,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("medicare_part_b_premium", PERIOD)[0] == pytest.approx(2_220)


def test_medicare_part_b_premium_is_zero_when_msp_covers_standard_premium():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=2_220,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("medicare_part_b_premium", PERIOD)[0] == pytest.approx(0)


def test_medicare_cost_uses_gross_part_b_before_msp_offset():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=2_220,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("medicare_part_b_premium", PERIOD)[0] == pytest.approx(0)
    assert sim.calculate("medicare_cost", PERIOD)[0] == pytest.approx(12_280)


def test_medicare_part_b_premium_is_zero_when_not_enrolled():
    sim = make_simulation(
        medicare_enrolled=False,
        gross_part_b_premium=2_220,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(0)
    assert sim.calculate("medicare_part_b_premium", PERIOD)[0] == pytest.approx(0)
    assert sim.calculate("gross_medicare_part_b_premium", PERIOD)[0] == pytest.approx(
        2_220
    )
    assert sim.calculate("gross_medicare_part_b_premium_if_enrolled", PERIOD)[
        0
    ] == pytest.approx(0)


def test_msp_part_b_premium_coverage_scales_with_eligible_months():
    monthly_eligibility = {
        f"{PERIOD}-{month:02d}": month <= 3 for month in range(1, 13)
    }
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "is_medicare_eligible": {PERIOD: True},
                    "medicare_enrolled": {PERIOD: True},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "msp_income_eligible": monthly_eligibility,
                    "msp_asset_eligible": monthly_eligibility,
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(
        555,
        abs=1e-6,
    )


def test_historical_msp_asset_eligibility_uses_federal_default():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {"person": {"ssi_countable_resources": {"2014": 0}}},
            "households": {"household": {"members": ["person"], "state_code": "AR"}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("msp_asset_eligible", "2014-01")[0]


def test_historical_msp_asset_limits_before_2013():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "below_limit": {"ssi_countable_resources": {"2012": 6_940}},
                "above_limit": {"ssi_countable_resources": {"2012": 7_000}},
                "spouse_1": {"ssi_countable_resources": {"2012": 5_000}},
                "spouse_2": {"ssi_countable_resources": {"2012": 5_500}},
            },
            "households": {
                "household": {
                    "members": [
                        "below_limit",
                        "above_limit",
                        "spouse_1",
                        "spouse_2",
                    ],
                    "state_code": "AR",
                }
            },
            "tax_units": {
                "tax_unit_1": {"members": ["below_limit"]},
                "tax_unit_2": {"members": ["above_limit"]},
                "tax_unit_3": {"members": ["spouse_1", "spouse_2"]},
            },
            "spm_units": {
                "spm_unit_1": {"members": ["below_limit"]},
                "spm_unit_2": {"members": ["above_limit"]},
                "spm_unit_3": {"members": ["spouse_1", "spouse_2"]},
            },
            "families": {
                "family_1": {"members": ["below_limit"]},
                "family_2": {"members": ["above_limit"]},
                "family_3": {"members": ["spouse_1", "spouse_2"]},
            },
            "marital_units": {
                "marital_unit_1": {"members": ["below_limit"]},
                "marital_unit_2": {"members": ["above_limit"]},
                "marital_unit_3": {"members": ["spouse_1", "spouse_2"]},
            },
        },
    )

    assert sim.calculate("msp_asset_eligible", "2012-01").tolist() == [
        True,
        False,
        False,
        False,
    ]


def test_medicare_part_b_premium_does_not_depend_on_calculation_order():
    no_msp_eligibility = {
        f"{year}-{month:02d}": False
        for year in ("2025", "2026")
        for month in range(1, 13)
    }
    situation = {
        "people": {
            "person": {
                "age": {"2025": 65, "2026": 66},
                "is_medicare_eligible": {"2025": True, "2026": True},
                "medicare_enrolled": {"2025": True, "2026": True},
                "gross_medicare_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "base_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "msp_income_eligible": no_msp_eligibility,
                "msp_asset_eligible": no_msp_eligibility,
            }
        },
        "households": {"household": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
    }

    ordered_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    ordered_sim.calculate("medicare_part_b_premium", "2025")
    ordered_result = ordered_sim.calculate("medicare_part_b_premium", "2026")[0]

    fresh_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    fresh_result = fresh_sim.calculate("medicare_part_b_premium", "2026")[0]

    assert ordered_result == pytest.approx(fresh_result)
    assert ordered_result == pytest.approx(2_220)


def test_gross_medicare_part_b_premium_handles_direct_filing_status_inputs():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person_1": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
                "person_2": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
                "person_3": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
            },
            "households": {
                "household": {"members": ["person_1", "person_2", "person_3"]}
            },
            "tax_units": {
                "joint_tax_unit": {
                    "members": ["person_1", "person_2"],
                    "filing_status": {PERIOD: "JOINT"},
                    "adjusted_gross_income": {"2023": 1_000_000},
                },
                "single_tax_unit": {
                    "members": ["person_3"],
                    "filing_status": {PERIOD: "SINGLE"},
                    "adjusted_gross_income": {"2023": 50_000},
                },
            },
            "spm_units": {
                "spm_unit": {"members": ["person_1", "person_2", "person_3"]}
            },
            "families": {"family": {"members": ["person_1", "person_2", "person_3"]}},
            "marital_units": {
                "marital_unit_1": {"members": ["person_1", "person_2"]},
                "marital_unit_2": {"members": ["person_3"]},
            },
        },
    )

    result = sim.calculate("gross_medicare_part_b_premium", PERIOD)
    assert result[0] == pytest.approx(7_546.8)
    assert result[1] == pytest.approx(7_546.8)
    assert result[2] == pytest.approx(2_220)


def test_gross_medicare_part_b_premium_if_enrolled_preserves_irmaa():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=4_440,
        base_part_b_premium=2_220,
        msp_income_eligible=False,
        msp_asset_eligible=False,
    )

    assert sim.calculate("gross_medicare_part_b_premium_if_enrolled", PERIOD)[
        0
    ] == pytest.approx(4_440)
    assert sim.calculate("medicare_cost", PERIOD)[0] == pytest.approx(10_060)


def test_medicare_irmaa_magi_two_years_prior_falls_back_to_lagged_income():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 6_002},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "filing_status": {PERIOD: "SINGLE"},
                    "adjusted_gross_income": {"2023": 100_000},
                }
            },
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("medicare_irmaa_magi_two_years_prior", PERIOD)[
        0
    ] == pytest.approx(106_002)
    assert sim.calculate("gross_medicare_part_b_premium", PERIOD)[0] == pytest.approx(
        3_108
    )


def test_medicare_irmaa_magi_two_years_prior_input_drives_irmaa():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "filing_status": {PERIOD: "SINGLE"},
                    "adjusted_gross_income": {"2023": 50_000},
                    "medicare_irmaa_magi_two_years_prior": {PERIOD: 500_000},
                }
            },
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("medicare_irmaa_magi_two_years_prior", PERIOD)[
        0
    ] == pytest.approx(500_000)
    assert sim.calculate("gross_medicare_part_b_premium", PERIOD)[0] == pytest.approx(
        7_546.8
    )
