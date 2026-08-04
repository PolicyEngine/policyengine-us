from policyengine_us import Simulation


def test_data_provided_ssi_disability_criteria_is_used_directly():
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "meets_ssi_disability_criteria": {2024: True},
                    "is_disabled": {2024: False},
                }
            }
        }
    )

    result = simulation.calculate("meets_ssi_disability_criteria", 2024)

    assert result[0]


def test_broad_disability_does_not_populate_ssi_disability_criteria():
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "is_disabled": {2024: True},
                }
            }
        }
    )

    result = simulation.calculate("meets_ssi_disability_criteria", 2024)

    assert not result[0]
