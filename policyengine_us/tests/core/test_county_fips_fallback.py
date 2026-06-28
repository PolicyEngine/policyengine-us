from policyengine_us import Simulation


def _two_household_situation() -> dict:
    return {
        "people": {
            "person_1": {"age": {"2026": 30}},
            "person_2": {"age": {"2026": 40}},
        },
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
                "state_code": {"2026": "NY"},
                "county_fips": {"2026": "36059"},
            },
            "household_2": {
                "members": ["person_2"],
                "state_code": {"2026": "CA"},
                "county_fips": {"2026": "06037"},
            },
        },
    }


def test_county_with_valid_fips_skips_first_county_fallback():
    simulation = Simulation(situation=_two_household_situation())
    simulation.trace = True

    county_str = simulation.calculate("county_str", 2026)

    assert county_str.tolist() == [
        "NASSAU_COUNTY_NY",
        "LOS_ANGELES_COUNTY_CA",
    ]
    assert simulation.tracer.get_nb_requests("first_county_in_state") == 0


def test_county_with_missing_fips_uses_first_county_fallback():
    situation = _two_household_situation()
    situation["households"]["household_1"]["county_fips"] = {"2026": ""}
    situation["households"]["household_2"]["county_fips"] = {"2026": ""}
    simulation = Simulation(situation=situation)
    simulation.trace = True

    county_str = simulation.calculate("county_str", 2026)

    assert county_str.tolist() == [
        "ALBANY_COUNTY_NY",
        "ALAMEDA_COUNTY_CA",
    ]
    assert simulation.tracer.get_nb_requests("first_county_in_state") == 1


def test_county_with_mixed_fips_preserves_known_rows_and_falls_back():
    situation = _two_household_situation()
    situation["households"]["household_2"]["county_fips"] = {"2026": ""}
    simulation = Simulation(situation=situation)
    simulation.trace = True

    county_str = simulation.calculate("county_str", 2026)

    assert county_str.tolist() == [
        "NASSAU_COUNTY_NY",
        "ALAMEDA_COUNTY_CA",
    ]
    assert simulation.tracer.get_nb_requests("first_county_in_state") == 1
