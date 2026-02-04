from policyengine_us import Simulation


def test_meets_ssi_resource_test_microsim_branch():
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "ssi_resource_test_seed": {"2024": 0.1},
                },
                "person2": {
                    "ssi_resource_test_seed": {"2024": 0.9},
                },
            },
            "households": {
                "household1": {
                    "members": ["person1", "person2"],
                },
            },
        }
    )
    sim.dataset = "mock"
    result = sim.calculate("meets_ssi_resource_test", "2024")
    assert result[0] == True  # 0.1 < 0.4 pass_rate
    assert result[1] == False  # 0.9 >= 0.4 pass_rate
