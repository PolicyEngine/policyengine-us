"""Country Simulation input remapping is a Python API contract."""

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
