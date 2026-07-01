from policyengine_us import Simulation


def _single_person_situation(person: dict) -> dict:
    return {
        "people": {
            "person": person,
        },
        "tax_units": {
            "tax_unit": {"members": ["person"]},
        },
        "spm_units": {
            "spm_unit": {"members": ["person"]},
        },
        "families": {
            "family": {"members": ["person"]},
        },
        "households": {
            "household": {
                "members": ["person"],
                "state_code": {"2026": "CA"},
            },
        },
    }


def test_snap_student_ineligibility_skips_tanf_for_non_higher_ed_person():
    simulation = Simulation(
        situation=_single_person_situation(
            {
                "age": {"2026": 30},
                "is_full_time_college_student": {"2026": False},
                "is_part_time_college_student": {"2026": False},
            }
        )
    )
    simulation.trace = True

    is_ineligible_student = simulation.calculate("is_snap_ineligible_student", 2026)

    assert is_ineligible_student.tolist() == [False]
    assert simulation.tracer.get_nb_requests("tanf_person") == 0
    assert simulation.tracer.get_nb_requests("tanf") == 0
