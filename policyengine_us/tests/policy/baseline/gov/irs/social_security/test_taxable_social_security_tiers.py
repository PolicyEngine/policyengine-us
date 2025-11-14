import pytest
from policyengine_us import Simulation


def test_taxable_social_security_tier_1_zero_income():
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
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 0


def test_taxable_social_security_tier_1_below_threshold():
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
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 0


def test_taxable_social_security_tier_1_in_tier_1():
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
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 4_500


def test_taxable_social_security_tier_1_in_tier_2():
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
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 4_500


def test_taxable_social_security_tier_1_separate_cohabitating():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 20_000},
                    "employment_income": {"2024": 10_000},
                },
                "person2": {
                    "age": {"2024": 65},
                    "social_security": {"2024": 10_000},
                    "employment_income": {"2024": 5_000},
                },
            },
            "tax_units": {
                "tax_unit1": {
                    "members": ["person1"],
                    "filing_status": {"2024": "SEPARATE"},
                },
                "tax_unit2": {
                    "members": ["person2"],
                    "filing_status": {"2024": "SEPARATE"},
                },
            },
            "marital_units": {
                "marital_unit": {"members": ["person1", "person2"]}
            },
            "households": {"household": {"members": ["person1", "person2"]}},
        }
    )
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 0
    assert result[1] == 0


def test_taxable_social_security_tier_1_joint_filers():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 20_000},
                    "employment_income": {"2024": 15_000},
                },
                "person2": {
                    "age": {"2024": 65},
                    "social_security": {"2024": 10_000},
                    "employment_income": {"2024": 10_000},
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
    result = sim.calculate("taxable_social_security_tier_1", 2024)
    assert result[0] == 4_000


def test_taxable_social_security_tier_2_zero_income():
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
    result = sim.calculate("taxable_social_security_tier_2", 2024)
    assert result[0] == 0


def test_taxable_social_security_tier_2_in_tier_1_only():
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
    result = sim.calculate("taxable_social_security_tier_2", 2024)
    assert result[0] == 850


def test_taxable_social_security_tier_2_in_tier_2():
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
    result = sim.calculate("taxable_social_security_tier_2", 2024)
    assert result[0] == 21_000


def test_taxable_social_security_tier_2_high_income():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "age": {"2024": 67},
                    "social_security": {"2024": 40_000},
                    "employment_income": {"2024": 100_000},
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
    result = sim.calculate("taxable_social_security_tier_2", 2024)
    assert abs(result[0] - 29_500) < 100


def test_taxable_social_security_tier_2_joint_filers():
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
    result = sim.calculate("taxable_social_security_tier_2", 2024)
    assert result[0] == 28_000


def test_taxable_social_security_tiers_sum():
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
    tier1 = sim.calculate("taxable_social_security_tier_1", 2024)
    tier2 = sim.calculate("taxable_social_security_tier_2", 2024)
    total = sim.calculate("tax_unit_taxable_social_security", 2024)

    assert abs(total[0] - (tier1[0] + tier2[0])) < 0.01
