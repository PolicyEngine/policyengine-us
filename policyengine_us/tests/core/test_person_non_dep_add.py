import numpy as np
import pytest

from policyengine_core.model_api import add
from policyengine_core.periods import period as make_period
from policyengine_us import Simulation
from policyengine_us.model_api import person_non_dep_add


YEAR = 2025
PERIOD = make_period(YEAR)
MEDICAL = "oh_unreimbursed_medical_care_expense_deduction_person"
OWN_ITEMS = ["salt_refund_income", "taxable_interest_income"]


@pytest.fixture(scope="module")
def simulation():
    names = [
        "head",
        "spouse",
        "child",
        "single",
        "dependent",
        "childless_head",
        "childless_spouse",
    ]
    dependents = [False, False, True, False, True, False, False]
    members = {"joint": names[:3], "single": names[3:5], "childless": names[5:]}
    sim = Simulation(
        situation={
            "people": {
                name: {
                    "age": {YEAR: age},
                    "is_tax_unit_head": {YEAR: i in (0, 3, 5)},
                    "is_tax_unit_spouse": {YEAR: i in (1, 6)},
                    "is_tax_unit_dependent": {YEAR: dependent},
                }
                for i, (name, age, dependent) in enumerate(
                    zip(names, [45, 43, 10, 35, 7, 55, 53], dependents)
                )
            },
            "tax_units": {
                name: {
                    "members": people,
                    "filing_status": {YEAR: "SINGLE" if name == "single" else "JOINT"},
                }
                for name, people in members.items()
            },
            "marital_units": {
                "joint": {"members": names[:2]},
                "child": {"members": [names[2]]},
                "single": {"members": [names[3]]},
                "dependent": {"members": [names[4]]},
                "childless": {"members": names[5:]},
            },
            "families": {name: {"members": people} for name, people in members.items()},
            "spm_units": {
                name: {"members": people} for name, people in members.items()
            },
            "households": {
                name: {"members": people, "state_code": {YEAR: "OH"}}
                for name, people in members.items()
            },
        }
    )
    sim.set_input("salt_refund_income", YEAR, [100, 200, 300, 400, 500, 600, 700])
    sim.set_input("taxable_interest_income", YEAR, [1, 2, 3, 4, 5, 6, 7])
    sim.set_input(MEDICAL, YEAR, [10, 20, 30, 40, 50, 60, 70])
    sim.set_input("tax_unit_social_security", YEAR, [1_000, 2_000, 3_000])
    sim.set_input("employment_income", YEAR, np.full(len(names), 2**24))
    sim.set_input("self_employment_income", YEAR, np.ones(len(names)))
    sim.set_input("short_term_capital_gains", YEAR, np.full(len(names), -(2**24)))
    return sim


def test_masks_dependents_own_amounts(simulation):
    person = simulation.populations["person"]
    result = person_non_dep_add(person, PERIOD, OWN_ITEMS)
    np.testing.assert_array_equal(result, [101, 202, 0, 404, 0, 606, 707])


def test_keeps_named_medical_amounts_on_dependents(simulation):
    person = simulation.populations["person"]
    result = person_non_dep_add(
        person,
        PERIOD,
        OWN_ITEMS + [MEDICAL],
        include_dependents=[MEDICAL],
    )
    np.testing.assert_array_equal(result, [111, 222, 30, 444, 50, 666, 777])


def test_empty_sum_preserves_person_shape_and_float32(simulation):
    person = simulation.populations["person"]
    result = person_non_dep_add(person, PERIOD, [])
    assert result.shape == (person.count,)
    assert result.dtype == np.float32
    np.testing.assert_array_equal(result, np.zeros(person.count, dtype=np.float32))


@pytest.mark.parametrize("include_dependents", [(), ("tax_unit_social_security",)])
def test_rejects_group_variables_even_when_named_as_exceptions(
    simulation, include_dependents
):
    with pytest.raises(ValueError, match="tax_unit_social_security"):
        person_non_dep_add(
            simulation.populations["person"],
            PERIOD,
            ["tax_unit_social_security"],
            include_dependents=include_dependents,
        )


@pytest.mark.parametrize("variables", [[], OWN_ITEMS])
def test_rejects_a_tax_unit_population(simulation, variables):
    with pytest.raises(ValueError, match="person"):
        person_non_dep_add(simulation.populations["tax_unit"], PERIOD, variables)


def test_matches_add_rounding_in_tax_unit_without_dependents(simulation):
    person = simulation.populations["person"]
    variables = [
        "employment_income",
        "self_employment_income",
        "short_term_capital_gains",
    ]
    assert not person("is_tax_unit_dependent", PERIOD)[-2:].any()
    expected = add(person, PERIOD, variables)[-2:]
    result = person_non_dep_add(person, PERIOD, variables)[-2:]
    # float32 rounds 2**24 + 1 to 2**24 before subtracting 2**24.
    np.testing.assert_array_equal(expected, np.zeros(2, dtype=np.float32))
    np.testing.assert_array_equal(result, expected)
    assert result.dtype == expected.dtype == np.float32
