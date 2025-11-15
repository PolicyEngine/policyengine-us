import pytest
from policyengine_us import Simulation


def test_tob_revenue_total_with_taxable_ss():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 30_000},
                    "employment_income": {"2024": 50_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_total", 2024)
    assert result[0] > 0


def test_tob_revenue_total_zero_income():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 0},
                    "employment_income": {"2024": 0},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_total", 2024)
    assert result[0] == 0


def test_tob_revenue_total_below_threshold():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 10_000},
                    "employment_income": {"2024": 5_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_total", 2024)
    assert result[0] == 0


def test_tob_revenue_medicare_hi_with_tier_2():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 30_000},
                    "employment_income": {"2024": 50_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_medicare_hi", 2024)
    assert result[0] > 0


def test_tob_revenue_medicare_hi_zero_income():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 0},
                    "employment_income": {"2024": 0},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_medicare_hi", 2024)
    assert result[0] == 0


def test_tob_revenue_medicare_hi_tier_1_only():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 30_000},
                    "employment_income": {"2024": 20_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_medicare_hi", 2024)
    assert result[0] >= 0


def test_tob_revenue_oasdi_with_tier_1():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 30_000},
                    "employment_income": {"2024": 50_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_oasdi", 2024)
    assert result[0] > 0


def test_tob_revenue_oasdi_zero_income():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 0},
                    "employment_income": {"2024": 0},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_oasdi", 2024)
    assert result[0] == 0


def test_tob_revenue_oasdi_only_tier_1():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 20_000},
                    "employment_income": {"2024": 30_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    result = sim.calculate("tob_revenue_oasdi", 2024)
    assert result[0] > 0


def test_tob_revenue_joint_filers():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 25_000},
                    "employment_income": {"2024": 35_000},
                },
                "person2": {
                    "age": {"2024": 65},
                    "social_security": {"2024": 15_000},
                    "employment_income": {"2024": 30_000},
                },
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1", "person2"],
                    "filing_status": {"2024": "JOINT"},
                }
            },
            "marital_units": {
                "marital_unit": {"members": ["person1", "person2"]}
            },
            "households": {"household": {"members": ["person1", "person2"]}},
        }
    )
    total_result = sim.calculate("tob_revenue_total", 2024)
    medicare_result = sim.calculate("tob_revenue_medicare_hi", 2024)
    oasdi_result = sim.calculate("tob_revenue_oasdi", 2024)

    assert total_result[0] > 0
    assert medicare_result[0] > 0
    assert oasdi_result[0] > 0
    assert abs(total_result[0] - (medicare_result[0] + oasdi_result[0])) < 1


def test_tob_revenue_total_multiple_calls():
    """Test that calling tob_revenue_total multiple times works correctly."""
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 30_000},
                    "employment_income": {"2024": 50_000},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )
    # Call twice to ensure branch cleanup works
    result1 = sim.calculate("tob_revenue_total", 2024)
    result2 = sim.calculate("tob_revenue_total", 2024)
    assert result1[0] == result2[0]
    assert result1[0] > 0
