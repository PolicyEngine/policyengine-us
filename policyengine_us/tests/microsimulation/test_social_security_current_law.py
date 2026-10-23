"""Differential compatibility with the four original public benefit inputs.

Python is required for constructor, Core builder, dataset, cache/branch and
export APIs that YAML cannot exercise.  The reference restores the original
four pure input definitions and disables only the new constructor migration;
all other current-law policy and wrapper behavior is identical.  One model
clone is shared read-only across the module.  Every population has two people,
with no external dataset, and only the neutral-reform branches copy policy.
Local runtime/memory measurements are reported with the PR's test receipt.
"""

from copy import deepcopy
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from policyengine_core.periods import YEAR
from policyengine_core.reforms import Reform
from policyengine_core.simulations import SimulationBuilder
from policyengine_core.variables import Variable

from policyengine_us import Microsimulation, Simulation
from policyengine_us.system import system
from policyengine_us.tools.period_branch import drop_inherited_values
from policyengine_us.tools.social_security_inputs import (
    SOCIAL_SECURITY_COMPONENTS,
    export_source_inputs,
    reload_source_inputs,
)


# All six social_security* variables present before this change, including
# the payroll-tax base whose name shares the benefit prefix.
PREEXISTING_SOCIAL_SECURITY = (
    *SOCIAL_SECURITY_COMPONENTS,
    "social_security",
    "social_security_taxable_self_employment_income",
)
DOWNSTREAM = (
    "taxable_social_security",
    "tax_unit_taxable_social_security",
    "adjusted_gross_income",
    "income_tax",
    "employee_social_security_tax",
    "employer_social_security_tax",
    "self_employment_social_security_tax",
    "ssi_unearned_income",
    "ssi",
    "snap_unearned_income",
    "snap",
    "medicare_irmaa_tax_year_magi",
    "medicare_irmaa_magi_two_years_prior",
    "medicare_irmaa_magi",
    "medicare_part_b_premium",
)
OUTPUTS = (*PREEXISTING_SOCIAL_SECURITY, *DOWNSTREAM)
NAMES = ("retiree", "disabled")
AMOUNTS = ((24_000, 0, 1_800, 600), (0, 6_000, 1_200, 300))


class HouseholdMicrosimulation(Microsimulation):
    default_dataset = None


@pytest.fixture(scope="module")
def original_input_system():
    """Restore main's input contracts, including effective per-capita growth."""
    original = system.clone()
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        reported = original.variables[f"{public_name}_reported"]
        input_class = type(
            public_name,
            (Variable,),
            {
                "value_type": reported.value_type,
                "entity": reported.entity,
                "definition_period": YEAR,
                "unit": reported.unit,
                "label": public_name,
                "uprating": reported.uprating,
            },
        )
        original.replace_variable(input_class)
        restored = original.variables[public_name]
        assert restored.is_input_variable()
        assert restored.uprating == reported.uprating
        assert restored.uprating.endswith("social_security_per_capita")
    return original


def situation(*, source="public", years=(2024, 2026), include_benefits=True):
    people = {}
    for index, name in enumerate(NAMES):
        person = {
            "age": {year: (70 if index == 0 else 45) + year - 2024 for year in years},
            "employment_income": {2024: 15_000 if index == 0 else 0},
            "self_employment_income": {2024: 3_000 if index == 0 else 0},
            "taxable_interest_income": {2024: 50_000 if index == 0 else 10},
            "is_disabled": {2024: index == 1},
            "takes_up_ssi_if_eligible": {2024: True},
        }
        if include_benefits:
            for public_name, amount in zip(SOCIAL_SECURITY_COMPONENTS, AMOUNTS[index]):
                name_to_store = (
                    f"{public_name}_reported" if source == "reported" else public_name
                )
                person[name_to_store] = {
                    year: amount * (1 if year == 2024 else 1.07) for year in years
                }
        people[name] = person
    result = {"people": people}
    for plural in ("households", "tax_units", "spm_units", "families", "marital_units"):
        result[plural] = {name: {"members": [name]} for name in NAMES}
    for household in result["households"].values():
        household["state_code"] = {year: "TX" for year in years}
    for spm_unit in result["spm_units"].values():
        spm_unit["takes_up_snap_if_eligible"] = {2024: True}
    return result


def reference_simulation(original_input_system, wrapper=Simulation, **kwargs):
    # Both wrappers retain all their existing income/geography preparation.
    # Only this PR's compatibility migration is absent from the reference.
    with patch(
        "policyengine_us.system.migrate_social_security_inputs", return_value=set()
    ):
        return wrapper(tax_benefit_system=original_input_system, **kwargs)


def assert_equal_outputs(current, original, requests, variables=OUTPUTS):
    for period in requests:
        for variable in variables:
            np.testing.assert_array_equal(
                np.asarray(current.calculate(variable, period)),
                np.asarray(original.calculate(variable, period)),
                err_msg=f"Current-law difference for {variable}, {period}",
            )


@pytest.mark.parametrize(
    "requests",
    [
        ("2024-12", 2026, "2025-03", 2024, 2025, "2026-08"),
        ("2026-08", 2025, 2024, "2025-03", 2026, "2024-12"),
    ],
    ids=("month-first-forward", "month-first-reverse"),
)
def test_household_current_law_matches_original_through_years_and_months(
    original_input_system, requests
):
    inputs = situation()
    original = reference_simulation(original_input_system, situation=deepcopy(inputs))
    current = Simulation(situation=inputs, tax_benefit_system=system)
    assert_equal_outputs(current, original, requests)

    # The supplied 2024 source must be read again for 2026 IRMAA, even after
    # calculating 2026 income and a different source amount for that year.
    np.testing.assert_array_equal(
        current.calculate("medicare_irmaa_magi_two_years_prior", 2026),
        current.calculate("medicare_irmaa_tax_year_magi", 2024),
    )
    assert not np.array_equal(
        current.calculate("medicare_irmaa_tax_year_magi", 2026),
        current.calculate("medicare_irmaa_tax_year_magi", 2024),
    )


def dataset_frame():
    """The dataset loader itself sets the stored public columns as inputs."""
    data = {"person_id": [1, 2]}
    for entity in ("household", "tax_unit", "spm_unit", "family", "marital_unit"):
        data[f"person_{entity}_id"] = [1, 2]
        data[f"{entity}_id"] = [1, 2]
    for year in (2024, 2026):
        data[f"age__{year}"] = [70 + year - 2024, 45 + year - 2024]
        data[f"state_fips__{year}"] = [48, 48]
        for component_index, public_name in enumerate(SOCIAL_SECURITY_COMPONENTS):
            data[f"{public_name}__{year}"] = [
                amounts[component_index] * (1 if year == 2024 else 1.07)
                for amounts in AMOUNTS
            ]
    data["employment_income__2024"] = [15_000, 0]
    data["self_employment_income__2024"] = [3_000, 0]
    data["taxable_interest_income__2024"] = [50_000, 10]
    data["is_disabled__2024"] = [False, True]
    data["takes_up_ssi_if_eligible__2024"] = [True, True]
    data["takes_up_snap_if_eligible__2024"] = [True, True]
    return pd.DataFrame(data)


def test_dataset_loader_current_law_matches_original(original_input_system):
    frame = dataset_frame()
    original = reference_simulation(
        original_input_system, Microsimulation, dataset=frame.copy(deep=True)
    )
    current = Microsimulation(dataset=frame, tax_benefit_system=system)
    assert_equal_outputs(current, original, ("2025-06", 2026, 2024, 2025))


@pytest.mark.parametrize("ingress", ["core_builder", "set_input"])
def test_core_builder_and_dataset_style_source_writes_match_original(
    original_input_system, ingress
):
    if ingress == "core_builder":
        original_situation = situation()
        current_situation = situation(source="reported")
    else:
        original_situation = situation(include_benefits=False)
        current_situation = deepcopy(original_situation)
    original = SimulationBuilder().build_from_dict(
        original_input_system, original_situation
    )
    current = SimulationBuilder().build_from_dict(system, current_situation)
    if ingress == "set_input":
        for component_index, public_name in enumerate(SOCIAL_SECURITY_COMPONENTS):
            for year in (2024, 2026):
                values = [
                    amounts[component_index] * (1 if year == 2024 else 1.07)
                    for amounts in AMOUNTS
                ]
                original.set_input(public_name, year, values)
                current.set_input(f"{public_name}_reported", year, values)
    assert_equal_outputs(current, original, ("2026-11", 2025, 2024, 2026))


def test_clones_and_neutral_reform_branches_match_original(original_input_system):
    original = reference_simulation(original_input_system, situation=situation())
    current = Simulation(situation=situation(), tax_benefit_system=system)
    assert_equal_outputs(current, original, (2024, 2026))

    # Warm-cache clones and ordinary branches should preserve the source
    # uprating path as well as any final public override applied later.
    for current_copy, original_copy in (
        (
            current.clone(clone_tax_benefit_system=False),
            original.clone(clone_tax_benefit_system=False),
        ),
        (current.get_branch("copy"), original.get_branch("copy")),
    ):
        current_copy.set_input("social_security_retirement", 2026, [0, 123])
        original_copy.set_input("social_security_retirement", 2026, [0, 123])
        drop_inherited_values(current_copy)
        drop_inherited_values(original_copy)
        assert_equal_outputs(current_copy, original_copy, (2026, "2025-07"))

    # Register an actual no-change parameter reform after outputs were
    # cached. This exercises reform replay and invalidation, while copying
    # policy only for these two branches and preserving the read-only models.
    neutral = Reform.from_dict(
        {"gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0}}
    )
    original_reform = original.get_branch("neutral_reform", clone_system=True)
    current_reform = current.get_branch("neutral_reform", clone_system=True)
    original_reform.apply_reform(neutral)
    current_reform.apply_reform(neutral)
    assert_equal_outputs(current_reform, original_reform, (2025, 2026))
    assert_equal_outputs(current, original, (2024, 2026))


def test_legacy_extraction_reload_matches_original(original_input_system):
    inputs = situation(years=(2024,))
    original = reference_simulation(
        original_input_system, HouseholdMicrosimulation, situation=deepcopy(inputs)
    )
    current = HouseholdMicrosimulation(situation=inputs, tax_benefit_system=system)
    original_payload = original.extract_person(0)
    current_payload = current.extract_person(0)
    original_reload = reference_simulation(
        original_input_system, situation=original_payload
    )
    current_reload = Simulation(situation=current_payload, tax_benefit_system=system)
    assert_equal_outputs(current_reload, original_reload, ("2024-10", 2024, 2025))
    for public_name, amount in zip(SOCIAL_SECURITY_COMPONENTS, AMOUNTS[0]):
        assert current_reload.calculate(public_name, 2024)[0] == amount


def test_complete_source_and_final_override_reload_matches_original(
    original_input_system,
):
    original = reference_simulation(original_input_system, situation=situation())
    current = Simulation(situation=situation(), tax_benefit_system=system)
    # An unsupplied, calculated year must remain a calculation after export.
    assert_equal_outputs(current, original, (2025,))
    for simulation in (original, current):
        simulation.set_input("social_security_retirement", 2027, [0, 123])
        simulation.set_input("social_security", 2027, [9_999, 0])
    original_payload = export_source_inputs(original)
    current_payload = export_source_inputs(current)
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        reported = current_payload["sources"]["people"]["retiree"][
            f"{public_name}_reported"
        ]
        assert set(reported) == {"2024", "2026"}
    with patch(
        "policyengine_us.system.migrate_social_security_inputs", return_value=set()
    ):
        original_reload = reload_source_inputs(
            original_payload, tax_benefit_system=original_input_system
        )
    current_reload = reload_source_inputs(current_payload, tax_benefit_system=system)
    requests = ("2027-08", 2026, 2024, 2025, 2027)
    assert_equal_outputs(current_reload, original_reload, requests)
    assert_equal_outputs(current_reload, current, requests)


def test_later_reported_write_updates_a_fresh_branch_without_changing_parent(
    original_input_system,
):
    current = Simulation(situation=situation(), tax_benefit_system=system)
    original = reference_simulation(original_input_system, situation=situation())
    assert_equal_outputs(current, original, (2024,))
    parent_keys = set(current._user_input_keys)
    current_branch = current.get_branch("updated_reported")
    original_branch = original.get_branch("updated_original")
    current_branch.set_input("social_security_retirement_reported", 2024, [30000, 2400])
    original_branch.set_input("social_security_retirement", 2024, [30000, 2400])
    drop_inherited_values(current_branch)
    drop_inherited_values(original_branch)
    assert_equal_outputs(current_branch, original_branch, (2024, 2025))
    assert current._user_input_keys == parent_keys
    np.testing.assert_array_equal(
        current.calculate("social_security_retirement", 2024), [24000, 0]
    )
    reloaded = reload_source_inputs(
        export_source_inputs(current_branch), tax_benefit_system=system
    )
    assert_equal_outputs(reloaded, current_branch, (2024, 2025))


@pytest.mark.parametrize("wrapper", [Simulation, HouseholdMicrosimulation])
def test_constructor_created_baseline_keeps_migrated_uprating(
    original_input_system,
    wrapper,
):
    # Core creates its automatic baseline before wrapper migration. A source
    # present only in 2024 must still uprate into 2025 on that baseline.
    neutral = Reform.from_dict(
        {"gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0}}
    )
    inputs = situation(years=(2024,))
    # Isolate this source migration from the existing wage/self-employment
    # constructor moves, which Core's pre-wrapper baseline does not perform.
    for person in inputs["people"].values():
        person.pop("employment_income")
        person.pop("self_employment_income")
    original = reference_simulation(
        original_input_system, wrapper, situation=deepcopy(inputs)
    )
    current = wrapper(situation=inputs, tax_benefit_system=system, reform=neutral)
    assert current.baseline is not None
    assert_equal_outputs(current.baseline, original, (2024, "2025-06", 2025))
    assert_equal_outputs(current, original, (2024, 2025))
    for public in SOCIAL_SECURITY_COMPONENTS:
        assert not current.baseline._get_set_input_periods(public)
        assert current.baseline._get_set_input_periods(f"{public}_reported")


@pytest.mark.parametrize("wrapper", [Simulation, HouseholdMicrosimulation])
def test_monthly_input_normalization_and_exact_multi_year_reads_match_original(
    original_input_system, wrapper
):
    inputs = situation(include_benefits=False)
    for person in inputs["people"].values():
        person["social_security_retirement"] = {2024: 12_000, "2024-07": 500}
        person["social_security_disability"] = {"2024-07": 300}
        person["social_security_survivors"] = {"year:2024:2": 2_000}
    original = reference_simulation(
        original_input_system, wrapper, situation=deepcopy(inputs)
    )
    current = wrapper(situation=inputs, tax_benefit_system=system)
    # Core's default FLOW input handler maps July to a rolling YEAR starting
    # in July. It does not store an exact MONTH on these annual variables.
    periods = current._get_set_input_periods("social_security_retirement_reported")
    assert {str(period) for period in periods} == {"2024", "year:2024-07"}
    assert all(period.unit == YEAR and period.size == 1 for period in periods)
    requests = ("2024-07", "year:2024-07", 2024, "2024-06", "year:2024:2")
    for public in SOCIAL_SECURITY_COMPONENTS[:2]:
        assert_equal_outputs(current, original, requests[:-1], variables=(public,))
    assert_equal_outputs(
        current, original, ("year:2024:2",), variables=("social_security_survivors",)
    )
    reloaded = reload_source_inputs(
        export_source_inputs(current), tax_benefit_system=system
    )
    for public in SOCIAL_SECURITY_COMPONENTS[:2]:
        assert_equal_outputs(reloaded, original, requests[:-1], variables=(public,))
    assert_equal_outputs(
        reloaded, original, ("year:2024:2",), variables=("social_security_survivors",)
    )
