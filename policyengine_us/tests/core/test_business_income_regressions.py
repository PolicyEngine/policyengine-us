import pytest

from policyengine_us import Simulation


def test_simulation_moves_self_employment_input_before_lsr():
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "self_employment_income": 10_000,
                },
            },
        },
    )

    assert simulation.calculate("self_employment_income_before_lsr", 2024)[0] == 10_000
    assert simulation.calculate("self_employment_income", 2024)[0] == 10_000


def test_simulation_moves_sstb_self_employment_input_before_lsr():
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "sstb_self_employment_income": 10_000,
                },
            },
        },
    )

    assert (
        simulation.calculate("sstb_self_employment_income_before_lsr", 2024)[0]
        == 10_000
    )
    assert simulation.calculate("sstb_self_employment_income", 2024)[0] == 10_000


def test_taxable_self_employment_income_uses_farm_operations_income():
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "farm_operations_income": 10_000,
                },
            },
        },
    )

    assert simulation.calculate("taxable_self_employment_income", 2024)[
        0
    ] == pytest.approx(9_235)


def test_taxable_self_employment_income_excludes_schedule_j_farm_income():
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "farm_income": 10_000,
                },
            },
        },
    )

    assert simulation.calculate("taxable_self_employment_income", 2024)[0] == 0
