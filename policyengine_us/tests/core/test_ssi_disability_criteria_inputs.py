from policyengine_us import Simulation


def test_data_provided_ssi_disability_criteria_carries_to_future_years():
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "is_disabled": {2024: False, 2026: False},
                    "meets_ssi_disability_criteria": {2024: True},
                }
            }
        }
    )

    result = simulation.calculate("meets_ssi_disability_criteria", 2026)

    assert result[0]


def test_formula_derived_ssi_disability_criteria_allows_later_disabled_input():
    simulation = Simulation(
        situation={
            "people": {
                "person1": {
                    "is_disabled": {2024: False, 2026: True},
                }
            }
        }
    )

    assert not simulation.calculate("meets_ssi_disability_criteria", 2024)[0]

    result = simulation.calculate("meets_ssi_disability_criteria", 2026)

    assert result[0]
