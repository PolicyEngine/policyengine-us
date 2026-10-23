"""Input compatibility, branch isolation and complete source round trips.

These cases need Python because YAML bypasses PE-US constructors and cannot
exercise cloning, stored-input bookkeeping or source export. They reuse the
read-only country model and use one person, without loading population data.
"""

import json

import numpy as np
import pandas as pd
import pytest
from policyengine_core.simulations import SimulationBuilder

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.economic_assumptions import MICRODATA_UPRATING_OVERRIDES
from policyengine_us.system import system
from policyengine_us.tools.period_branch import drop_inherited_values
from policyengine_us.tools.social_security_inputs import (
    SOCIAL_SECURITY_COMPONENTS,
    export_source_inputs,
    reload_source_inputs,
)


class HouseholdMicrosimulation(Microsimulation):
    """Exercise the actual wrapper with a household instead of its default data."""

    default_dataset = None


WRAPPERS = (Simulation, HouseholdMicrosimulation)
FACTOR = "social_security_across_the_board_factor"


def situation(inputs):
    return {
        "people": {"person": {"age": {2024: 70, 2025: 71, 2026: 72}, **inputs}},
        "households": {"household": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
    }


def make_simulation(wrapper=Simulation, inputs=None):
    return wrapper(situation=situation(inputs or {}), tax_benefit_system=system)


def amount(simulation, name, period):
    return np.asarray(simulation.calculate(name, period))[0]


def input_periods(simulation, name):
    return {str(period) for period in simulation._get_set_input_periods(name)}


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_constructor_precedence_is_per_component_and_period(wrapper):
    inputs = {}
    for index, public in enumerate(SOCIAL_SECURITY_COMPONENTS, 1):
        inputs[public] = {2024: index * 1_000, 2026: index * 3_000}
        inputs[f"{public}_reported"] = {2025: index * 1_100, 2026: index * 1_200}
    simulation = make_simulation(wrapper, inputs)
    for year in (2024, 2025, 2026):
        simulation.set_input(FACTOR, year, [1.1])
    for index, public in enumerate(SOCIAL_SECURITY_COMPONENTS, 1):
        reported = f"{public}_reported"
        assert input_periods(simulation, public) == {"2026"}
        assert input_periods(simulation, reported) == {"2024", "2025", "2026"}
        assert amount(simulation, public, 2024) == pytest.approx(index * 1_100)
        assert amount(simulation, public, 2025) == pytest.approx(index * 1_210)
        assert amount(simulation, reported, 2026) == index * 1_200
        assert amount(simulation, public, 2026) == index * 3_000
        assert public in simulation.input_variables
        assert reported in simulation.input_variables


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_constructor_zero_and_aggregate_are_explicit_inputs(wrapper):
    inputs = {
        SOCIAL_SECURITY_COMPONENTS[0]: {2024: 0},
        f"{SOCIAL_SECURITY_COMPONENTS[1]}_reported": {2024: 0},
        SOCIAL_SECURITY_COMPONENTS[2]: {2024: 0},
        f"{SOCIAL_SECURITY_COMPONENTS[2]}_reported": {2024: 500},
        "social_security": {2024: 123},
    }
    simulation = make_simulation(wrapper, inputs)
    simulation.set_input(FACTOR, 2024, [1.5])
    for public in SOCIAL_SECURITY_COMPONENTS:
        assert amount(simulation, public, 2024) == 0
    assert amount(simulation, "social_security", 2024) == 123
    assert SOCIAL_SECURITY_COMPONENTS[0] not in simulation.input_variables
    assert f"{SOCIAL_SECURITY_COMPONENTS[0]}_reported" in simulation.input_variables


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_later_public_override_survives_clones_and_cache_clear(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    assert amount(simulation, public, 2024) == 12_000
    simulation.set_input(public, 2024, [0])
    original_keys = set(simulation._user_input_keys)
    for copy in (
        simulation.clone(clone_tax_benefit_system=False),
        simulation.get_branch("override"),
    ):
        drop_inherited_values(copy)
        assert amount(copy, public, 2024) == 0
        copy.set_input(public, 2024, [42])
        drop_inherited_values(copy)
        assert amount(copy, public, 2024) == 42
        assert simulation._user_input_keys == original_keys
        assert amount(simulation, public, 2024) == 0
    assert amount(simulation, f"{public}_reported", 2024) == 12_000


def test_core_builder_public_inputs_are_final_overrides():
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = SimulationBuilder().build_from_dict(
        system,
        situation(
            {
                f"{retirement}_reported": {2024: 12_000},
                disability: {2024: 777},
                FACTOR: {2024: 1.1},
            }
        ),
    )
    assert amount(simulation, retirement, 2024) == pytest.approx(13_200)
    assert amount(simulation, disability, 2024) == 777
    assert input_periods(simulation, disability) == {"2024"}
    simulation.set_input(retirement, 2024, [0])
    assert amount(simulation, retirement, 2024) == 0


def test_dataset_constructor_migrates_stored_original_columns():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    frame = pd.DataFrame(
        {
            "person_id": [1],
            **{
                f"person_{entity}_id": [1]
                for entity in (
                    "household",
                    "tax_unit",
                    "spm_unit",
                    "family",
                    "marital_unit",
                )
            },
            **{
                f"{entity}_id": [1]
                for entity in (
                    "household",
                    "tax_unit",
                    "spm_unit",
                    "family",
                    "marital_unit",
                )
            },
            f"{public}__2024": [12_000],
            f"{public}__2026": [14_000],
            f"{public}_reported__2026": [13_000],
        }
    )
    simulation = Microsimulation(dataset=frame, tax_benefit_system=system)
    simulation.set_input(FACTOR, 2024, [1.1])
    assert amount(simulation, public, 2024) == pytest.approx(13_200)
    assert amount(simulation, public, 2026) == 14_000
    assert input_periods(simulation, public) == {"2026"}
    assert input_periods(simulation, f"{public}_reported") == {"2024", "2026"}
    # Loader-time public writes migrate; later writes remain final outputs.
    simulation.set_input(public, 2024, [0])
    assert amount(simulation, public, 2024) == 0
    assert amount(simulation, f"{public}_reported", 2024) == 12_000
    reloaded = reload_source_inputs(
        export_source_inputs(simulation), tax_benefit_system=system
    )
    assert amount(reloaded, public, 2024) == 0
    assert amount(reloaded, f"{public}_reported", 2024) == 12_000


def test_complete_snapshot_preserves_histories_and_separate_final_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={
            f"{public}_reported": {2024: 12_000, 2026: 14_000},
            public: {2026: 6_500},
            f"{public}_source": {2024: "reported", 2026: "reported"},
            "ss_aime_input": {2024: 1_000, 2026: 2_000},
            "employment_income": {2024: 10_000, 2026: 20_000},
        }
    )
    # A calculated intervening year must never become a reported source.
    amount(simulation, public, 2025)
    simulation.set_input(public, 2027, [0])
    payload = json.loads(json.dumps(export_source_inputs(simulation)))
    person = payload["sources"]["people"]["person"]
    assert set(person[f"{public}_reported"]) == {"2024", "2026"}
    assert public not in person
    assert set(payload["overrides"][public]) == {"2026", "2027"}
    assert person["ss_aime_input"] == {"2024": 1_000, "2026": 2_000}
    reloaded = reload_source_inputs(payload, tax_benefit_system=system)
    for name in (public, f"{public}_reported", "ss_aime_input", "employment_income"):
        for year in (2024, 2025, 2026, 2027):
            assert amount(reloaded, name, year) == pytest.approx(
                amount(simulation, name, year)
            )
    assert input_periods(reloaded, public) == {"2026", "2027"}
    assert export_source_inputs(reloaded)["overrides"][public]["2027"] == [0]


def test_legacy_extraction_uses_reported_sources_and_months_keep_flow_conversion():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(HouseholdMicrosimulation, {public: {2024: 12_000}})
    extracted = simulation.extract_person(0)
    person = next(iter(extracted["people"].values()))
    assert f"{public}_reported" in person
    assert public not in person
    reloaded = Simulation(situation=extracted, tax_benefit_system=system)
    for month_first in (False, True):
        copy = reloaded.clone(clone_tax_benefit_system=False)
        if month_first:
            assert amount(copy, public, "2024-07") == 1_000
        assert amount(copy, public, 2024) == 12_000
        assert amount(copy, public, "2024-07") == 1_000


def test_reported_twins_are_pure_and_original_dataset_names_keep_their_uprater():
    for public in SOCIAL_SECURITY_COMPONENTS:
        original = system.get_variable(public)
        reported = system.get_variable(f"{public}_reported")
        assert not original.is_input_variable()
        assert original.uprating is None
        assert reported.is_input_variable()
        assert reported.label == original.label
        assert not reported.formulas and not reported.adds and not reported.subtracts
        assert reported.uprating.endswith("social_security_per_capita")
        assert (
            MICRODATA_UPRATING_OVERRIDES[public]
            == "calibration.gov.irs.soi.social_security"
        )


@pytest.mark.parametrize(
    "source", ["supplied_aime", "supplied_pia", "supplied_ratio_survivor", "history"]
)
def test_reserved_sources_fail_explicitly_instead_of_using_reported_fallback(source):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={f"{public}_source": {2024: source}, f"{public}_reported": {2024: 0}}
    )
    with pytest.raises(NotImplementedError, match="reserved"):
        simulation.calculate(public, 2024)


def test_oasi_only_cut_rejects_unidentified_positive_dependent_stream():
    from policyengine_core.reforms import Reform

    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.payable.share": {"2024": 0.8},
            "gov.contrib.ssa.benefit_levers.payable.oasi_only": {"2024": True},
        }
    )
    simulation = Simulation(
        situation=situation({"social_security_dependents_reported": {2024: 500}}),
        reform=reform,
        tax_benefit_system=system,
    )
    with pytest.raises(ValueError, match="dependent benefit fund"):
        simulation.calculate("social_security_dependents", 2024)


def test_parameter_reform_registration_order_preserves_stable_public_formula():
    from policyengine_core.reforms import Reform

    across = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                "2024": 2024
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0.1},
        }
    )
    payable = Reform.from_dict(
        {"gov.contrib.ssa.benefit_levers.payable.share": {"2024": 0.8}}
    )
    first = Simulation(
        situation=situation({"social_security_retirement_reported": {2024: 12000}}),
        reform=(across, payable),
        tax_benefit_system=system,
    )
    second = Simulation(
        situation=situation({"social_security_retirement_reported": {2024: 12000}}),
        reform=(payable, across),
        tax_benefit_system=system,
    )
    assert amount(first, "social_security_retirement", 2024) == pytest.approx(10560)
    assert amount(second, "social_security_retirement", 2024) == pytest.approx(10560)
    assert (
        first.tax_benefit_system.variables["social_security_retirement"].formulas
        == second.tax_benefit_system.variables["social_security_retirement"].formulas
    )


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_exact_multi_year_sources_keep_keys_uniform_factors_and_overrides(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    simulation = make_simulation(wrapper, {public: {multi_year: 24_000}})
    assert input_periods(simulation, public) == set()
    assert input_periods(simulation, reported) == {multi_year}
    assert amount(simulation, public, multi_year) == 24_000
    parent_keys = set(simulation._user_input_keys)
    uniform = simulation.get_branch("uniform_multi_year")
    for year in (2024, 2025):
        uniform.set_input(FACTOR, year, [1.1])
    drop_inherited_values(uniform)
    assert amount(uniform, public, multi_year) == pytest.approx(26_400)
    assert simulation._user_input_keys == parent_keys
    assert amount(simulation, public, multi_year) == 24_000
    reloaded = reload_source_inputs(
        export_source_inputs(uniform), tax_benefit_system=system
    )
    assert input_periods(reloaded, reported) == {multi_year}
    assert amount(reloaded, public, multi_year) == pytest.approx(26_400)
    uniform.set_input(public, multi_year, [0])
    clone = uniform.clone(clone_tax_benefit_system=False)
    drop_inherited_values(clone)
    assert amount(clone, public, multi_year) == 0
    override_reload = reload_source_inputs(
        export_source_inputs(clone), tax_benefit_system=system
    )
    assert amount(override_reload, public, multi_year) == 0
    assert amount(override_reload, reported, multi_year) == 24_000


def test_exact_multi_year_both_names_and_neutralization_keep_core_precedence(
    monkeypatch,
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    simulation = make_simulation(
        inputs={public: {multi_year: 123}, reported: {multi_year: 24_000}}
    )
    simulation.set_input(FACTOR, 2024, [1.1])
    simulation.set_input(FACTOR, 2025, [0.8])
    assert amount(simulation, public, multi_year) == 123
    assert amount(simulation, reported, multi_year) == 24_000
    neutralized = make_simulation(inputs={reported: {multi_year: 24_000}})
    with monkeypatch.context() as context:
        context.setattr(system.variables[public], "is_neutralized", True)
        assert amount(neutralized, public, multi_year) == 0


def test_exact_multi_year_source_rejects_differing_annual_factors_without_allocation():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    multi_year = "year:2024:2"
    simulation = make_simulation(inputs={public: {multi_year: 24_000}})
    simulation.set_input(FACTOR, 2024, [1.1])
    simulation.set_input(FACTOR, 2025, [0.8])
    with pytest.raises(ValueError, match="separately supplied annual source amounts"):
        simulation.calculate(public, multi_year)
    assert input_periods(simulation, f"{public}_reported") == {multi_year}


def test_containing_period_migration_preserves_sources_and_inner_final_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(
        inputs={
            public: {2024: 123, "year:2024:10": 100_000, "year:2024:2": 24_000},
            reported: {2024: 12_000},
        }
    )
    assert input_periods(simulation, public) == {"2024"}
    assert input_periods(simulation, reported) == {
        "2024",
        "year:2024:2",
        "year:2024:10",
    }
    assert amount(simulation, public, 2024) == 123
    assert amount(simulation, reported, 2024) == 12_000
    assert amount(simulation, public, "year:2024:2") == 24_000
    assert amount(simulation, reported, "year:2024:10") == 100_000


def test_multi_year_selected_base_input_and_neutralization_take_precedence(monkeypatch):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported, base = f"{public}_reported", f"{public}_base"
    multi_year = "year:2024:2"
    simulation = make_simulation(
        inputs={reported: {multi_year: 24_000}, base: {multi_year: 6_000}}
    )
    for year in (2024, 2025):
        simulation.set_input(FACTOR, year, [1.1])
    assert amount(simulation, public, multi_year) == pytest.approx(6_600)
    reloaded = reload_source_inputs(
        export_source_inputs(simulation), tax_benefit_system=system
    )
    assert amount(reloaded, public, multi_year) == pytest.approx(6_600)

    base_only = make_simulation(inputs={base: {multi_year: 6_000}})
    assert amount(base_only, public, multi_year) == 6_000
    neutralized = make_simulation(
        inputs={reported: {multi_year: 24_000}, base: {multi_year: 6_000}}
    )
    neutralized.set_input(FACTOR, 2024, [1.1])
    neutralized.set_input(FACTOR, 2025, [0.8])
    with monkeypatch.context() as context:
        context.setattr(system.variables[base], "is_neutralized", True)
        assert amount(neutralized, public, multi_year) == 0


def test_multi_year_reported_total_rejects_partial_base_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={
            f"{public}_reported": {"year:2024:2": 24_000},
            f"{public}_base": {2024: 6_000},
        }
    )
    with pytest.raises(ValueError, match="base overrides for other periods"):
        simulation.calculate(public, "year:2024:2")


def test_multi_year_zero_rows_do_not_require_annual_allocation():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    inputs = {
        "people": {
            "positive": {reported: {multi_year: 24_000}},
            "zero": {reported: {multi_year: 0}},
        },
        "households": {"household": {"members": ["positive", "zero"]}},
    }
    simulation = Simulation(situation=inputs, tax_benefit_system=system)
    simulation.set_input(FACTOR, 2024, [1.1, 1.1])
    simulation.set_input(FACTOR, 2025, [1.1, 0.8])
    np.testing.assert_allclose(simulation.calculate(public, multi_year), [26_400, 0])
    all_zero = simulation.get_branch("all_zero_multi_year")
    all_zero.set_input(reported, multi_year, [0, 0])
    drop_inherited_values(all_zero)
    np.testing.assert_array_equal(all_zero.calculate(public, multi_year), [0, 0])


def test_dimensionless_benefit_factors_keep_annual_levels_on_monthly_requests():
    factor_names = (
        "social_security_across_the_board_factor",
        "social_security_payable_factor",
        *(
            f"{component}_{suffix}"
            for component in SOCIAL_SECURITY_COMPONENTS
            for suffix in ("joint_cola_factor", "pia_ratio_factor", "payable_factor")
        ),
    )
    simulation = make_simulation()
    for name in factor_names:
        assert system.variables[name].unit == "/1"
        assert amount(simulation, name, "2024-07") == 1
        assert amount(simulation, name, 2024) == 1
    supplied = simulation.get_branch("supplied_dimensionless_factors")
    for name in factor_names:
        supplied.set_input(name, 2024, [1.2])
    drop_inherited_values(supplied)
    for name in factor_names:
        assert amount(supplied, name, "2024-07") == pytest.approx(1.2)
        assert amount(supplied, name, 2024) == pytest.approx(1.2)
