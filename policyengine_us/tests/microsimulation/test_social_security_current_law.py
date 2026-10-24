"""Compare legacy public ingress with an unmodified main checkout.

The same probe runs in separate Python processes against this checkout and
main. No variable definitions or input names are substituted in the reference.
An unmodified pre-feature main checkout is required. Set PE_US_MAIN_CHECKOUT
to that checkout, or make the reviewed main commit or a pre-feature main ref
available locally (the fixture archives it without changing either checkout).
"""

import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import numpy as np
import pytest

COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
BENEFITS = (*COMPONENTS, "social_security")
DOWNSTREAM = (
    "social_security_taxable_self_employment_income",
    "taxable_social_security",
    "tax_unit_taxable_social_security",
    "adjusted_gross_income",
    "income_tax",
    "household_net_income",
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
INGRESS_OUTCOMES = (
    *COMPONENTS,
    "income_tax",
    "household_net_income",
    "medicare_irmaa_magi_two_years_prior",
)
AMOUNTS = ((12_000, 0, 1_800, 600), (0, 6_000, 1_200, 300))
REVIEWED_MAIN_SHA = "8986e05cab65d56435a23df1910e2d35f2c5f5bf"


def situation(*, include_benefits=True):
    """Identical legacy public-name inputs for every checkout and wrapper."""
    result = {"people": {}}
    for index, name in enumerate(("retiree", "disabled")):
        person = {
            "age": {2024: 70 if index == 0 else 45, 2026: 72 if index == 0 else 47},
            "employment_income": {2024: 15_000 if index == 0 else 0},
            "self_employment_income": {2024: 3_000 if index == 0 else 0},
            "taxable_interest_income": {2024: 50_000 if index == 0 else 10},
            "is_disabled": {2024: index == 1},
            "takes_up_ssi_if_eligible": {2024: True},
        }
        if include_benefits:
            for component, amount in zip(COMPONENTS, AMOUNTS[index]):
                person[component] = {2024: amount}
        result["people"][name] = person
    for plural in ("households", "tax_units", "spm_units", "families", "marital_units"):
        result[plural] = {name: {"members": [name]} for name in result["people"]}
    for household in result["households"].values():
        household["state_code"] = {2024: "TX", 2026: "TX"}
    for spm_unit in result["spm_units"].values():
        spm_unit["takes_up_snap_if_eligible"] = {2024: True}
    return result


def extraction_situation():
    """The review's single-person, single-input-period extraction reproducer."""
    result = {
        "people": {
            "retiree": {
                "age": {2024: 70},
                "social_security_retirement": {2024: 12_000},
                "taxable_interest_income": {2024: 40_000},
                "takes_up_ssi_if_eligible": {2024: True},
            }
        }
    }
    for plural in ("households", "tax_units", "spm_units", "families", "marital_units"):
        result[plural] = {"group": {"members": ["retiree"]}}
    result["households"]["group"]["state_code"] = {2024: "TX"}
    return result


def _snapshot(simulation, periods, variables=BENEFITS):
    return {
        f"{variable}@{period}": np.asarray(
            simulation.calculate(variable, period)
        ).tolist()
        for period in periods
        for variable in variables
    }


def _write_h5(path):
    """Variable-centric v2pop-style H5, with public columns in its scored year."""
    import h5py

    ids = np.array([1, 2])
    columns = {"person_id": ids, "age": [72, 47]}
    for entity in ("household", "tax_unit", "spm_unit", "family", "marital_unit"):
        columns[f"person_{entity}_id"] = ids
        columns[f"{entity}_id"] = ids
        columns[f"{entity}_weight"] = [1.0, 1.0]
    columns["state_fips"] = [48, 48]
    for index, component in enumerate(COMPONENTS):
        columns[component] = [amounts[index] for amounts in AMOUNTS]
    with h5py.File(path, "w") as stored:
        for name, values in columns.items():
            stored.create_dataset(f"{name}/2026", data=values)


def _probe():
    """Only imports from the checkout selected through the subprocess path."""
    import gc

    import pandas as pd
    import yaml
    from policyengine_core.data import Dataset
    from policyengine_core.periods import period
    from policyengine_core.reforms import Reform
    from policyengine_core.simulations import (
        Simulation as CoreSimulation,
        SimulationBuilder,
    )
    from policyengine_us import Microsimulation, Simulation
    from policyengine_us.system import system

    class HouseholdMicrosimulation(Microsimulation):
        default_dataset = None

    class HolderSetterSimulation(Simulation):
        def set_input(self, variable, input_period, value):
            if variable in COMPONENTS and hasattr(self, "input_variables"):
                return self.get_holder(variable).set_input(
                    period(input_period), np.asarray(value), self.branch_name
                )
            return super().set_input(variable, input_period, value)

    has_levers = "social_security_retirement_reported" in system.variables
    neutral = (
        Reform.from_dict(
            {"gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0}}
        )
        if has_levers
        else None
    )
    result = {}
    for label, wrapper in (
        ("simulation", Simulation),
        ("microsimulation", HouseholdMicrosimulation),
    ):
        simulation = wrapper(situation=situation(), tax_benefit_system=system)
        result[f"constructor_{label}"] = _snapshot(simulation, (2024, 2026, "2025-07"))
        if label == "simulation":
            result["constructor_downstream"] = _snapshot(
                simulation, (2024, 2026), DOWNSTREAM
            )
            assert (
                result["constructor_downstream"][
                    "medicare_irmaa_magi_two_years_prior@2026"
                ]
                == result["constructor_downstream"]["medicare_irmaa_tax_year_magi@2024"]
            )
        del simulation
        gc.collect()

        # A fresh period has no explicit twin. The later public override
        # must be final in 2026 and seed main's uprating path into 2027.
        simulation = wrapper(situation=situation(), tax_benefit_system=system)
        simulation.set_input("social_security_retirement", 2026, [24_000, 0])
        result[f"later_override_{label}"] = _snapshot(simulation, (2026, 2027))
        if label == "simulation":
            # The complete-history helper is new in this change. On main,
            # the equivalent reference is the same live source/override state.
            try:
                from policyengine_us.tools.social_security_inputs import (
                    export_source_inputs,
                    reload_source_inputs,
                )
            except ImportError:
                if has_levers:
                    raise
                result["complete_export_reload"] = _snapshot(
                    simulation, (2024, 2025, 2026, 2027)
                )
                simulation.set_input("social_security_retirement", 2026, [36_000, 0])
                result["complete_export_rewrite"] = _snapshot(simulation, (2026, 2027))
            else:
                payload = export_source_inputs(simulation)
                assert payload["overrides"]["social_security_retirement"]["2026"] == [
                    24_000,
                    0,
                ]
                reloaded = reload_source_inputs(payload, tax_benefit_system=system)
                result["complete_export_reload"] = _snapshot(
                    reloaded, (2024, 2025, 2026, 2027)
                )
                assert result["complete_export_reload"] == _snapshot(
                    simulation, (2024, 2025, 2026, 2027)
                )
                reloaded.set_input("social_security_retirement", 2026, [36_000, 0])
                result["complete_export_rewrite"] = _snapshot(reloaded, (2026, 2027))
                del reloaded
        del simulation
        gc.collect()

        # A same-period later public write updates the twin originally moved
        # from public ingress. An explicitly supplied twin retains priority
        # in the separate precedence tests. Extraction must preserve this
        # origin as well as the final override for a subsequent public write.
        simulation = wrapper(
            situation=extraction_situation(), tax_benefit_system=system
        )
        simulation.set_input("social_security_retirement", 2024, [24_000])
        # Extract before calculations introduce earlier lookback cache periods
        # into Core's legacy first-known-period selection.
        payload = simulation.extract_person(0)
        extracted_person = next(iter(payload["people"].values()))
        assert extracted_person["age"] == {"2024": 70}
        reloaded = Simulation(situation=payload, tax_benefit_system=system)
        live = _snapshot(simulation, (2024,), (*BENEFITS, *DOWNSTREAM))
        extracted = _snapshot(reloaded, (2024,), (*BENEFITS, *DOWNSTREAM))
        expected = {key: values[:1] for key, values in live.items()}
        assert extracted == expected, {
            key: {"live": expected[key], "reloaded": extracted[key]}
            for key in expected
            if extracted[key] != expected[key]
        }
        result[f"extraction_reload_{label}"] = extracted
        assert live["medicare_irmaa_tax_year_magi@2024"][0] > 0
        for candidate in (simulation, reloaded):
            # PE-US carries the supplied age forward. Keep this retired
            # household eligible for Medicare in the future lookback checks.
            for year in (2026, 2027):
                np.testing.assert_array_equal(candidate.calculate("age", year), [70])
        live_future = _snapshot(simulation, (2026, 2027), (*BENEFITS, *DOWNSTREAM))
        result[f"same_period_override_{label}"] = live_future
        assert (
            live_future["medicare_irmaa_magi_two_years_prior@2026"]
            == live["medicare_irmaa_tax_year_magi@2024"]
        )
        extracted_future = _snapshot(reloaded, (2026, 2027), (*BENEFITS, *DOWNSTREAM))
        expected_future = {key: values[:1] for key, values in live_future.items()}
        assert extracted_future == expected_future, {
            key: {"live": expected_future[key], "reloaded": extracted_future[key]}
            for key in expected_future
            if extracted_future[key] != expected_future[key]
        }
        result[f"extraction_future_reload_{label}"] = extracted_future
        reloaded.set_input("social_security_retirement", 2024, [36_000])
        result[f"extraction_rewrite_{label}"] = _snapshot(
            reloaded, (2024, 2026, 2027), (*BENEFITS, *DOWNSTREAM)
        )
        del simulation, reloaded
        gc.collect()

        # Core constructs a baseline before the US wrapper returns. The
        # current tree's neutral lever reform must migrate that clone too;
        # unmodified main supplies the same current-law values directly.
        inputs = situation()
        for person in inputs["people"].values():
            # Existing wage/self-employment constructor migrations run after
            # Core creates its baseline. Isolate the benefit ingress here.
            person.pop("employment_income")
            person.pop("self_employment_income")
        simulation = wrapper(
            situation=inputs, tax_benefit_system=system, reform=neutral
        )
        baseline = simulation.baseline if has_levers else simulation
        assert baseline is not None
        result[f"automatic_baseline_{label}"] = _snapshot(
            baseline, (2024, 2026, "2025-07")
        )
        result[f"neutral_constructor_{label}"] = _snapshot(simulation, (2024, 2026))
        del baseline, simulation
        gc.collect()

    # YAML reaches Core's builder directly, bypassing both US constructors.
    yaml_inputs = yaml.safe_load(yaml.safe_dump(situation()))
    simulation = SimulationBuilder().build_from_dict(system, yaml_inputs)
    result["yaml_core_builder"] = _snapshot(simulation, (2024, 2026))
    result["yaml_core_downstream"] = _snapshot(simulation, (2026,), DOWNSTREAM)
    del simulation
    gc.collect()

    simulation = SimulationBuilder().build_from_entities(system, situation())
    result["core_entities_builder"] = _snapshot(simulation, (2024, 2026))
    del simulation
    gc.collect()

    for route, method in (
        ("core_variables_builder", "build_from_variables"),
        ("core_flat_dict_builder", "build_from_dict"),
    ):
        inputs = {"age": {2024: [70, 45]}}
        for index, component in enumerate(COMPONENTS):
            inputs[component] = {2024: [amounts[index] for amounts in AMOUNTS]}
        simulation = getattr(SimulationBuilder(), method)(system, inputs)
        result[route] = _snapshot(simulation, (2024, 2026))
        del simulation
        gc.collect()

    simulation = SimulationBuilder().build_from_dict(
        system, situation(include_benefits=False)
    )
    for index, component in enumerate(COMPONENTS):
        simulation.set_input(component, 2024, [amounts[index] for amounts in AMOUNTS])
    result["public_set_input"] = _snapshot(simulation, (2024, 2026))
    del simulation
    gc.collect()

    # Both paths bypass CoreSimulation.set_input. The public holder must
    # still seed future benefits and keep a later write final in its year.
    for route, wrapper in (
        ("direct_public_holder", Simulation),
        ("subclass_public_set_input_holder", HolderSetterSimulation),
    ):
        inputs = extraction_situation()
        del inputs["people"]["retiree"]["social_security_retirement"]
        simulation = wrapper(situation=inputs, tax_benefit_system=system)
        if route == "direct_public_holder":
            simulation.get_holder("social_security_retirement").set_input(
                period(2024), np.array([12_000]), simulation.branch_name
            )
        else:
            simulation.set_input("social_security_retirement", 2024, [12_000])
        result[route] = _snapshot(simulation, (2024, 2026), INGRESS_OUTCOMES)
        del simulation
        gc.collect()

    # Raw Core dataset construction runs without either US wrapper or the
    # situation builder's migration path.
    columns = {"person_id": [1]}
    for entity in ("household", "tax_unit", "spm_unit", "family", "marital_unit"):
        columns[f"person_{entity}_id"] = [1]
        columns[f"{entity}_id"] = [1]
    columns.update(
        {
            "age__2024": [70],
            "social_security_retirement__2024": [12_000],
        }
    )
    simulation = CoreSimulation(
        dataset=pd.DataFrame(columns),
        tax_benefit_system=system,
        default_input_period=2024,
        default_calculation_period=2024,
    )
    result["raw_core_dataset"] = _snapshot(simulation, (2024, 2026), INGRESS_OUTCOMES)
    del simulation
    gc.collect()

    # Preserve Core's exact compound input and its annual/downstream
    # behavior. This simulation has no US wrapper.
    inputs = extraction_situation()
    inputs["people"]["retiree"]["social_security_retirement"] = {"year:2024:2": 24_000}
    simulation = SimulationBuilder().build_from_dict(system, inputs)
    result["core_builder_exact_multiyear"] = _snapshot(
        simulation, ("year:2024:2",), ("social_security_retirement",)
    )
    result["core_builder_exact_multiyear"].update(
        _snapshot(simulation, (2024, 2026), INGRESS_OUTCOMES)
    )
    del simulation
    gc.collect()

    for route in ("clone", "branch"):
        simulation = Simulation(situation=situation(), tax_benefit_system=system)
        original_inputs = list(simulation.input_variables)
        parent = _snapshot(simulation, (2024, 2026))
        copied = (
            simulation.clone(clone_tax_benefit_system=False)
            if route == "clone"
            else simulation.get_branch("public_override")
        )
        copied.set_input("social_security_retirement", 2026, [24_000, 0])
        result[route] = _snapshot(copied, (2026, 2027))
        assert _snapshot(simulation, (2024, 2026)) == parent
        assert simulation.input_variables == original_inputs
        if has_levers:
            assert copied.input_variables is not simulation.input_variables
        result[f"{route}_parent"] = _snapshot(simulation, (2024, 2026))
        if route == "branch":
            reformed = simulation.get_branch("neutral_reform", clone_system=True)
            if neutral is not None:
                reformed.apply_reform(neutral)
            result["neutral_reform_branch"] = _snapshot(reformed, (2024, 2026))
            del reformed
        del simulation, copied
        gc.collect()

    for label, wrapper in (
        ("simulation", Simulation),
        ("microsimulation", HouseholdMicrosimulation),
    ):
        inputs = situation(include_benefits=False)
        for person in inputs["people"].values():
            person["social_security_retirement"] = {2024: 12_000, "2024-07": 500}
            person["social_security_disability"] = {"2024-07": 300}
            person["social_security_survivors"] = {"year:2024:2": 2_000}
        for household in inputs["households"].values():
            household["household_weight"] = {"year:2024:2": 1}
        simulation = wrapper(situation=inputs, tax_benefit_system=system)
        result[f"monthly_{label}"] = _snapshot(
            simulation,
            ("2024-07", "year:2024-07", 2024, "2024-06"),
            COMPONENTS[:2],
        )
        result[f"multi_year_{label}"] = _snapshot(
            simulation, ("year:2024:2",), ("social_security_survivors",)
        )
        del simulation
        gc.collect()

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "public_components_2026.h5"
        _write_h5(path)
        dataset = Dataset.from_file(path)
        assert dataset.data_format == Dataset.TIME_PERIOD_ARRAYS
        simulation = Microsimulation(dataset=dataset, tax_benefit_system=system)
        result["h5_scored_year"] = _snapshot(
            simulation, (2026,), (*BENEFITS, *DOWNSTREAM)
        )
        for index, component in enumerate(COMPONENTS):
            np.testing.assert_array_equal(
                np.asarray(simulation.calculate(component, 2026)),
                [amounts[index] for amounts in AMOUNTS],
                err_msg=f"H5 scored-year source was not loaded for {component}",
            )
        # Main has no benefit-lever parameter. Its role here is the unchanged
        # current-law reference; the lever assertion runs in the current tree.
        if has_levers:
            reform = Reform.from_dict(
                {
                    "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                        "2026": 2026
                    },
                    "gov.contrib.ssa.benefit_levers.across_the_board.rate": {
                        "2026": 0.08
                    },
                }
            )
            reformed = Microsimulation(
                dataset=dataset, tax_benefit_system=system, reform=reform
            )
            for component in COMPONENTS:
                expected = np.asarray(simulation.calculate(component, 2026)) * 1.08
                np.testing.assert_array_equal(
                    np.asarray(reformed.calculate(component, 2026)), expected
                )
            np.testing.assert_allclose(
                np.asarray(reformed.calculate("social_security", 2026)),
                np.asarray(simulation.calculate("social_security", 2026)) * 1.08,
                rtol=1e-7,
                atol=0,
            )
    return result


def _main_checkout(current, directory):
    reported_files = {f"{component}_reported.py" for component in COMPONENTS}
    configured = os.environ.get("PE_US_MAIN_CHECKOUT")
    if configured:
        checkout = Path(configured).resolve()
        assert checkout != current.resolve(), (
            "PE_US_MAIN_CHECKOUT must be a separate unmodified pre-feature main checkout"
        )
        assert (checkout / "policyengine_us").is_dir(), configured
        if (checkout / ".git").exists():
            status = subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=checkout,
                text=True,
            )
            assert not status, "PE_US_MAIN_CHECKOUT must have no tracked changes"
            if (current / ".git").exists():
                current_head = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=current, text=True
                ).strip()
                reference_head = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
                ).strip()
                assert reference_head != current_head, (
                    "PE_US_MAIN_CHECKOUT must not use the current checkout's HEAD"
                )
        assert not any(
            path.name in reported_files
            for path in (checkout / "policyengine_us" / "variables").rglob(
                "*_reported.py"
            )
        ), "PE_US_MAIN_CHECKOUT must contain unmodified pre-feature main variables"
        return checkout
    for ref in (
        REVIEWED_MAIN_SHA,
        "refs/remotes/origin/main",
        "refs/remotes/gh/main",
        "refs/heads/main",
    ):
        exists = subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            cwd=current,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if exists.returncode == 0:
            names = subprocess.check_output(
                [
                    "git",
                    "ls-tree",
                    "-r",
                    "--name-only",
                    ref,
                    "policyengine_us/variables",
                ],
                cwd=current,
                text=True,
            )
            if any(Path(name).name in reported_files for name in names.splitlines()):
                continue
            archive = subprocess.check_output(["git", "archive", ref], cwd=current)
            checkout = directory / "main"
            checkout.mkdir()
            with tarfile.open(fileobj=io.BytesIO(archive)) as stored:
                stored.extractall(checkout, filter="data")
            return checkout
    pytest.skip(
        "Differential needs an unmodified pre-feature main checkout: set "
        "PE_US_MAIN_CHECKOUT or provide the reviewed main commit or a local "
        "origin/main, gh/main, or main ref without reported benefit variables"
    )


@pytest.fixture(scope="module")
def differential(tmp_path_factory):
    directory = tmp_path_factory.mktemp("social_security_differential")
    current = Path(__file__).resolve().parents[3]
    reference = _main_checkout(current, directory)
    results = []
    for label, checkout in (("current", current), ("main", reference)):
        destination = directory / f"{label}.json"
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(checkout)
        for variable in (
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ):
            environment[variable] = "4"
        environment["OMP_WAIT_POLICY"] = "PASSIVE"
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--probe",
                str(destination),
            ],
            cwd=checkout,
            env=environment,
            capture_output=True,
            text=True,
            timeout=420,
            check=False,
        )
        assert completed.returncode == 0, (
            f"{label} differential probe failed:\n"
            f"{completed.stdout[-4000:]}\n{completed.stderr[-8000:]}"
        )
        results.append(json.loads(destination.read_text()))
    return results


@pytest.mark.parametrize(
    "route",
    (
        "constructor_simulation",
        "constructor_microsimulation",
        "constructor_downstream",
        "later_override_simulation",
        "later_override_microsimulation",
        "extraction_reload_simulation",
        "extraction_reload_microsimulation",
        "same_period_override_simulation",
        "same_period_override_microsimulation",
        "extraction_future_reload_simulation",
        "extraction_future_reload_microsimulation",
        "extraction_rewrite_simulation",
        "extraction_rewrite_microsimulation",
        "automatic_baseline_simulation",
        "automatic_baseline_microsimulation",
        "neutral_constructor_simulation",
        "neutral_constructor_microsimulation",
        "complete_export_reload",
        "complete_export_rewrite",
        "yaml_core_builder",
        "yaml_core_downstream",
        "core_entities_builder",
        "core_variables_builder",
        "core_flat_dict_builder",
        "public_set_input",
        "direct_public_holder",
        "subclass_public_set_input_holder",
        "raw_core_dataset",
        "core_builder_exact_multiyear",
        "clone",
        "branch",
        "clone_parent",
        "branch_parent",
        "neutral_reform_branch",
        "monthly_simulation",
        "monthly_microsimulation",
        "multi_year_simulation",
        "multi_year_microsimulation",
        "h5_scored_year",
    ),
)
def test_legacy_public_ingress_matches_unmodified_main(differential, route):
    current, main = differential
    assert current[route].keys() == main[route].keys()
    for request in main[route]:
        np.testing.assert_array_equal(
            current[route][request],
            main[route][request],
            err_msg=f"Legacy public ingress differs on {route}: {request}",
        )


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--probe":
        raise SystemExit("Usage: test_social_security_current_law.py --probe OUTPUT")
    Path(sys.argv[2]).write_text(json.dumps(_probe()))
