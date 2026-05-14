from policyengine_us import Simulation


def _two_person_two_household_situation(
    person_a: dict,
    person_b: dict,
    *,
    state: str = "CA",
) -> dict:
    return {
        "people": {
            "a": person_a,
            "b": person_b,
        },
        "tax_units": {
            "tax_unit_a": {"members": ["a"]},
            "tax_unit_b": {"members": ["b"]},
        },
        "spm_units": {
            "spm_unit_a": {"members": ["a"]},
            "spm_unit_b": {"members": ["b"]},
        },
        "families": {
            "family_a": {"members": ["a"]},
            "family_b": {"members": ["b"]},
        },
        "households": {
            "household_a": {"members": ["a"], "state_code": {"2026": state}},
            "household_b": {"members": ["b"], "state_code": {"2026": state}},
        },
    }


def test_is_usda_disabled_reduces_per_person_not_across_simulation():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={
                "age": {"2026": 40},
                "social_security_disability": {"2026": 100},
            },
        )
    )

    assert simulation.calculate("is_usda_disabled", 2026).tolist() == [
        False,
        True,
    ]


def test_medicaid_medically_needy_category_reduces_per_person():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={"age": {"2026": 70}},
        )
    )

    assert simulation.calculate(
        "is_in_medicaid_medically_needy_category", 2026
    ).tolist() == [
        False,
        True,
    ]
