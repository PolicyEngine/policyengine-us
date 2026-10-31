"""Exact-year COLA overrides expire only in generated dataset years."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Simulation
from policyengine_us.data import USMultiYearDataset, USSingleYearDataset
from policyengine_us.data.economic_assumptions import (
    _apply_uprating,
    extend_single_year_dataset,
)
from policyengine_us.tests.unit.test_ss_cola_means_test import (
    COMPONENTS,
    _calculator_record,
    _record,
    _reform,
    _simulation,
    _situation,
)


OVERRIDES = tuple(
    f"social_security_{component}_cola_override" for component in COMPONENTS
) + ("ss_calculator_cola_override",)
LEGACY_WITHHELD = tuple(
    f"social_security_{component}_cola_withheld" for component in COMPONENTS
) + ("ss_calculator_withhold_cola",)


def _controls_dataset(year=2027):
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [1, 2, 3],
                **{name: [-1, 0, 1] for name in OVERRIDES},
                **{name: [False, True, False] for name in LEGACY_WITHHELD},
            }
        ),
        household=pd.DataFrame({"household_id": [1]}),
        tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        time_period=year,
    )


def _assert_generated_controls(dataset):
    for name in OVERRIDES:
        np.testing.assert_array_equal(dataset[2027].person[name], [-1, 0, 1])
        for year in (2028, 2029):
            np.testing.assert_array_equal(dataset[year].person[name], [-1, -1, -1])
    for year in dataset.years:
        for name in LEGACY_WITHHELD:
            np.testing.assert_array_equal(
                dataset[year].person[name], [False, True, False]
            )


def test_generated_years_reset_all_five_overrides_and_preserve_legacy_booleans():
    source = _controls_dataset()
    original = source.person.copy()
    extended = extend_single_year_dataset(
        source, end_year=2029, system=SimpleNamespace(variables={})
    )
    _assert_generated_controls(extended)
    pd.testing.assert_frame_equal(source.person, original)


def test_supplied_multiyear_decisions_survive_uprating_and_serialization(tmp_path):
    first = _controls_dataset()
    second = _controls_dataset(2028)
    for name in OVERRIDES:
        second.person[name] = [1, -1, 0]
    supplied = USMultiYearDataset(datasets=[first, second])
    uprated = _apply_uprating(supplied, system=SimpleNamespace(variables={}))
    path = str(tmp_path / "supplied_years.h5")
    uprated.save(path)
    restored = USMultiYearDataset(file_path=path)
    for year in supplied.years:
        pd.testing.assert_frame_equal(restored[year].person, supplied[year].person)


@pytest.mark.parametrize("from_file", [False, True])
def test_constructor_generation_routes_expire_overrides_without_running_microsim(
    from_file, tmp_path, monkeypatch
):
    # Exercise both constructor routes through the real extender. Stub Core's
    # constructor so this routing test neither loads nor runs a microsimulation.
    from policyengine_us import system as system_module
    from policyengine_us.tests.microsimulation.data.fixtures.test_extend_single_year_dataset import (
        make_mock_super_init,
    )

    source = _controls_dataset()
    dataset = source
    if from_file:
        dataset = str(tmp_path / "single_year.h5")
        source.save(dataset)
    captured = [None]
    monkeypatch.setattr(
        system_module.CoreMicrosimulation,
        "__init__",
        make_mock_super_init(system_module, captured=captured),
    )
    system_module.Microsimulation(dataset=dataset, dataset_end_year=2029)
    _assert_generated_controls(captured[0])


@pytest.fixture(scope="module")
def means_test_system():
    return _simulation(_situation(), _reform()).tax_benefit_system


@pytest.mark.parametrize("calculator", [False, True])
def test_generated_year_does_not_repeat_a_paid_cola_override(
    means_test_system, calculator
):
    record = _calculator_record("worker") if calculator else _record()
    row = {
        name: value[2027] if isinstance(value, dict) else value
        for name, value in record.items()
    }
    entities = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
    row.update(person_id=1, **{f"person_{entity}_id": 1 for entity in entities})
    override = (
        "ss_calculator_cola_override"
        if calculator
        else "social_security_retirement_cola_override"
    )
    row[override] = 0
    source = USSingleYearDataset(
        person=pd.DataFrame([row]),
        household=pd.DataFrame({"household_id": [1], "household_weight": [1.0]}),
        tax_unit=pd.DataFrame(
            {"tax_unit_id": [1], "social_security_cola_means_test_magi": [1_000_000]}
        ),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1]}),
        time_period=2027,
    )
    extended = extend_single_year_dataset(
        source, end_year=2028, system=means_test_system
    )
    if calculator:
        # PIA is a fixed eligibility-year source. Keep it fixed here so generic
        # monetary uprating cannot change the separate COLA-expiry comparison.
        for year in extended.years:
            extended[year].person["ss_calculator_supplied_pia"] = 1000
    simulation = Simulation(dataset=extended, tax_benefit_system=means_test_system)
    for year in (2026, 2027):
        simulation.set_input("social_security_cola_means_test_magi", year, [1_000_000])
    variable, period, expected = (
        ("ss_calculated_payment", "2028-01", 1036)
        if calculator
        else ("social_security_retirement", 2028, 12352.54)
    )
    np.testing.assert_allclose(
        simulation.calculate(variable, period), [expected], rtol=0, atol=0.01
    )
