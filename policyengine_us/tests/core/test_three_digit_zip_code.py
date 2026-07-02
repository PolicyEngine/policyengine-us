from policyengine_us import Simulation


def _situation(zip_codes: dict[str, str]) -> dict:
    return {
        "people": {name: {"age": {"2026": 30}} for name in ("person_1", "person_2")},
        "tax_units": {
            "tax_unit_1": {"members": ["person_1"]},
            "tax_unit_2": {"members": ["person_2"]},
        },
        "spm_units": {
            "spm_unit_1": {"members": ["person_1"]},
            "spm_unit_2": {"members": ["person_2"]},
        },
        "families": {
            "family_1": {"members": ["person_1"]},
            "family_2": {"members": ["person_2"]},
        },
        "households": {
            "household_1": {
                "members": ["person_1"],
                **(
                    {"zip_code": {"2026": zip_codes["household_1"]}}
                    if "household_1" in zip_codes
                    else {}
                ),
            },
            "household_2": {
                "members": ["person_2"],
                **(
                    {"zip_code": {"2026": zip_codes["household_2"]}}
                    if "household_2" in zip_codes
                    else {}
                ),
            },
        },
    }


def test_three_digit_zip_code_truncates_numeric_zip_codes():
    simulation = Simulation(
        situation=_situation({"household_1": "10001", "household_2": "90210"})
    )

    assert simulation.calculate("three_digit_zip_code", 2026).tolist() == [
        "100",
        "902",
    ]


def test_three_digit_zip_code_passes_non_numeric_values_through():
    # zip_code defaults to "UNKNOWN" when a dataset or situation stores no
    # zip codes; the three-digit derivation must not crash on it.
    simulation = Simulation(situation=_situation({"household_1": "10001"}))

    assert simulation.calculate("three_digit_zip_code", 2026).tolist() == [
        "100",
        "UNKNOWN",
    ]
