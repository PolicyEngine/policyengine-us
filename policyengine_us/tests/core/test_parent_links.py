from copy import deepcopy

import numpy as np

from policyengine_us import Simulation


def test_parent_links_are_scoped_to_interleaved_households():
    # Person IDs repeat across households, and linked/unlinked rows alternate.
    # Composition inputs isolate the non-filer branch from income exclusions.
    names = [
        "linked_parent",
        "legacy_parent",
        "linked_child",
        "legacy_child",
        "unrelated_child",
        "legacy_sibling",
    ]
    ages = [35, 45, 10, 8, 16, 13]
    incomes = [10_000.125, 20_000.375, 100.25, 300.125, 200.5, 400.25]
    people = {
        name: {
            "age": {"2026": age},
            "person_id": {"2026": person_id},
            "own_children_in_household": {"2026": own_children},
            "medicaid_uses_non_filer_rules": {"2026": True},
            "medicaid_household_income_member": {"2026": income},
            "medicaid_magi_person": {"2026": income},
            "medicaid_person_is_required_to_file": {"2026": True},
        }
        for name, age, income, person_id, own_children in zip(
            names, ages, incomes, [11, 11, 12, 12, 13, 13], [0, 2, 0, 0, 0, 0]
        )
    }
    people["linked_child"]["parent_1_id"] = {"2026": 11}
    groups = {
        "linked": ["linked_parent", "linked_child", "unrelated_child"],
        "legacy": ["legacy_parent", "legacy_child", "legacy_sibling"],
    }
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": {
                name: {"members": members} for name, members in groups.items()
            },
            "spm_units": {
                name: {"members": members} for name, members in groups.items()
            },
            "families": {
                name: {"members": members} for name, members in groups.items()
            },
            "marital_units": {name: {"members": [name]} for name in names},
            "households": {
                name: {"members": members, "state_code": {"2026": "OH"}}
                for name, members in groups.items()
            },
        }
    )

    np.testing.assert_array_equal(
        simulation.calculate("is_parent", 2026),
        [True, True, False, False, False, False],
    )
    np.testing.assert_array_equal(
        simulation.calculate("medicaid_household_size", 2026),
        [3, 3, 2, 3, 3, 3],
    )
    # Exact binary fractions expose cross-household joins without tolerances.
    # The unrelated child has no links and retains the family-sum fallback.
    np.testing.assert_array_equal(
        simulation.calculate("medicaid_household_income", 2026),
        [10_300.875, 20_700.75, 10_100.375, 20_700.75, 10_300.875, 20_700.75],
    )


def test_explicit_zero_parent_ids_exactly_match_omitted_inputs():
    situation = {
        "people": {
            "mother": {
                "age": {"2026": 35},
                "is_female": {"2026": True},
                "own_children_in_household": {"2026": 1},
                "employment_income": {"2026": 12_345.67},
            },
            "father": {
                "age": {"2026": 36},
                "is_female": {"2026": False},
                "own_children_in_household": {"2026": 1},
                "employment_income": {"2026": 23_456.78},
            },
            "child": {
                "age": {"2026": 10},
                "employment_income": {"2026": 600.11},
            },
        },
        "tax_units": {
            "mother": {
                "members": ["mother", "child"],
                "tax_unit_is_filer": {"2026": True},
            },
            "father": {
                "members": ["father"],
                "tax_unit_is_filer": {"2026": True},
            },
        },
        "spm_units": {"family": {"members": ["mother", "father", "child"]}},
        "families": {"family": {"members": ["mother", "father", "child"]}},
        "marital_units": {
            name: {"members": [name]} for name in ["mother", "father", "child"]
        },
        "households": {
            "household": {
                "members": ["mother", "father", "child"],
                "state_code": {"2026": "OH"},
            }
        },
    }
    explicit_zeros = deepcopy(situation)
    for inputs in explicit_zeros["people"].values():
        inputs["parent_1_id"] = {"2026": 0}
        inputs["parent_2_id"] = {"2026": 0}

    omitted = Simulation(situation=situation)
    zeros = Simulation(situation=explicit_zeros)
    for variable in [
        "is_parent",
        "is_mother",
        "is_father",
        "medicaid_claimed_by_parent_in_tax_unit",
        "medicaid_tax_dependent_exception_living_with_both_parents",
        "medicaid_uses_non_filer_rules",
        "medicaid_household_size",
        "medicaid_household_income",
        "is_medicaid_eligible",
    ]:
        np.testing.assert_array_equal(
            zeros.calculate(variable, 2026),
            omitted.calculate(variable, 2026),
            err_msg=variable,
        )

    np.testing.assert_array_equal(
        zeros.calculate("is_parent", 2026), [True, True, False]
    )
    np.testing.assert_array_equal(
        zeros.calculate("medicaid_uses_non_filer_rules", 2026), [False, False, True]
    )
    np.testing.assert_array_equal(
        zeros.calculate("medicaid_household_size", 2026), [2, 1, 3]
    )
