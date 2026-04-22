from types import SimpleNamespace

import numpy as np
import pytest

import policyengine_us.variables.gov.simulation.capital_gains_responses as capital_gains_module
import policyengine_us.variables.gov.simulation.labor_supply_response.income_elasticity_lsr as income_lsr_module
import policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response as labor_supply_module
import policyengine_us.variables.gov.simulation.labor_supply_response.self_employment_income_behavioral_response as self_employment_response_module
import policyengine_us.variables.gov.simulation.labor_supply_response.sstb_self_employment_income_behavioral_response as sstb_self_employment_response_module
import policyengine_us.variables.gov.simulation.labor_supply_response.substitution_elasticity_lsr as substitution_lsr_module
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    BEHAVIORAL_RESPONSE_INPUT_VARIABLES,
    BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES,
    calculate_income_lsr_effect,
    calculate_relative_capital_gains_mtr_change,
    calculate_relative_income_change,
    calculate_relative_wage_change,
    calculate_substitution_lsr_effect,
    earnings_before_lsr,
    get_behavioral_response_measurements,
)
from policyengine_us.variables.gov.simulation.capital_gains_responses import (
    adult_index_cg,
    capital_gains_elasticity,
    capital_gains_behavioral_response,
    relative_capital_gains_mtr_change,
)
from policyengine_us.variables.gov.simulation.labor_supply_response.income_elasticity_lsr import (
    income_elasticity_lsr,
)
from policyengine_us.variables.gov.simulation.labor_supply_response.labor_supply_behavioral_response import (
    labor_supply_behavioral_response,
)
from policyengine_us.variables.gov.simulation.labor_supply_response.substitution_elasticity_lsr import (
    substitution_elasticity_lsr,
)


class FakePopulation:
    def __init__(self, net_income, mtr, capital_gains_mtr):
        self.net_income = net_income
        self.mtr = mtr
        self.capital_gains_mtr = capital_gains_mtr

    def __call__(self, variable, period):
        if variable == "marginal_tax_rate":
            return self.mtr
        if variable == "marginal_tax_rate_on_capital_gains":
            return self.capital_gains_mtr
        raise AssertionError(f"Unexpected variable lookup: {variable}")

    def household(self, variable, period):
        if variable != "household_net_income":
            raise AssertionError(f"Unexpected household lookup: {variable}")
        return self.net_income


class FakeTaxBenefitSystem:
    def __init__(self):
        self.parameters = SimpleNamespace(simulation=object())
        self.neutralized_variables = []

    def neutralize_variable(self, variable):
        self.neutralized_variables.append(variable)


class FakeBranch:
    def __init__(self, population=None, child_branches=None):
        self.tax_benefit_system = FakeTaxBenefitSystem()
        self.populations = {"person": population} if population is not None else {}
        self.branches = {}
        self.child_branches = child_branches or {}
        self.input_calls = []
        self.get_branch_calls = []

    def set_input(self, variable, period, value):
        self.input_calls.append((variable, period, value))

    def get_branch(self, name, clone_system=False):
        self.get_branch_calls.append((name, clone_system))
        if name not in self.branches:
            self.branches[name] = self.child_branches[name]
        return self.branches[name]


class FakeSimulation:
    def __init__(self, measurement_branch, baseline_branch):
        self.measurement_branch = measurement_branch
        self.baseline_branch = baseline_branch
        self.branches = {}
        self.get_branch_calls = []
        self.macro_cache_read = True
        self.macro_cache_write = True

    def get_branch(self, name, clone_system=False):
        self.get_branch_calls.append((name, clone_system))
        if name not in self.branches:
            if name == BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH:
                self.branches[name] = self.measurement_branch
            elif name == "baseline":
                self.branches[name] = self.baseline_branch
            else:
                raise AssertionError(f"Unexpected branch lookup: {name}")
        return self.branches[name]


class FakePerson:
    def __init__(self, simulation):
        self.simulation = simulation
        self.count = 2
        self.entity = SimpleNamespace(
            is_person=True,
            key="person",
            plural="people",
        )
        self.entity.get_variable = lambda variable: SimpleNamespace(entity=self.entity)
        self.values = {
            "employment_income_before_lsr": np.array([50_000.0, 20_000.0]),
            "self_employment_income_before_lsr": np.array([0.0, 5_000.0]),
            "sstb_self_employment_income_before_lsr": np.array([0.0, 0.0]),
            "long_term_capital_gains_before_response": np.array([10_000.0, 500.0]),
        }

    def __call__(self, variable, period, options=None):
        return self.values[variable]


def make_parameters(
    *,
    income_change_bound=0.3,
    wage_change_bound=0.4,
    capital_gains_elasticity=-0.62,
    lsr_income_elasticity=-0.05,
    lsr_substitution_elasticity=0.25,
):
    return lambda period: SimpleNamespace(
        gov=SimpleNamespace(
            simulation=SimpleNamespace(
                labor_supply_responses=SimpleNamespace(
                    elasticities=SimpleNamespace(
                        income=lsr_income_elasticity,
                        substitution=SimpleNamespace(all=lsr_substitution_elasticity),
                    ),
                    bounds=SimpleNamespace(
                        income_change=income_change_bound,
                        effective_wage_rate_change=wage_change_bound,
                    ),
                ),
                capital_gains_responses=SimpleNamespace(
                    elasticity=capital_gains_elasticity
                ),
            )
        )
    )


def test_behavioral_response_measurements_use_one_neutralized_pass():
    period = 2026
    reform_measurement = FakeBranch(
        FakePopulation(
            net_income=np.array([100.0, 200.0]),
            mtr=np.array([0.25, 0.35]),
            capital_gains_mtr=np.array([0.18, 0.22]),
        )
    )
    baseline_measurement = FakeBranch(
        FakePopulation(
            net_income=np.array([90.0, 190.0]),
            mtr=np.array([0.2, 0.3]),
            capital_gains_mtr=np.array([0.15, 0.2]),
        )
    )
    baseline_parent = FakeBranch(
        child_branches={
            BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH: baseline_measurement
        }
    )
    simulation = FakeSimulation(reform_measurement, baseline_parent)
    person = FakePerson(simulation)

    measurements = get_behavioral_response_measurements(person, period)

    assert np.array_equal(measurements["reform_net_income"], np.array([100.0, 200.0]))
    assert np.array_equal(
        measurements["baseline_capital_gains_mtr"], np.array([0.15, 0.2])
    )
    assert simulation.get_branch_calls == [
        (BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, True),
        ("baseline", False),
    ]
    assert baseline_parent.get_branch_calls == [
        (BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, True)
    ]
    for branch in (reform_measurement, baseline_measurement):
        assert branch.tax_benefit_system.neutralized_variables == list(
            NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES
        )
        assert [call[0] for call in branch.input_calls] == list(
            BEHAVIORAL_RESPONSE_INPUT_VARIABLES
        )

    assert simulation.macro_cache_read is False
    assert simulation.macro_cache_write is False
    assert BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH not in simulation.branches
    assert (
        BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH not in baseline_parent.branches
    )

    cached = get_behavioral_response_measurements(person, period)
    assert cached is measurements
    assert simulation.get_branch_calls == [
        (BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, True),
        ("baseline", False),
    ]


def test_measurement_helper_calculations_clip_expected_values():
    measurements = {
        "baseline_net_income": np.array([100.0, 100.0]),
        "reform_net_income": np.array([1.0, 200.0]),
        "baseline_mtr": np.array([1.0, 0.2]),
        "reform_mtr": np.array([0.8, 0.4]),
        "baseline_capital_gains_mtr": np.array([0.0, 0.2]),
        "reform_capital_gains_mtr": np.array([0.1, 0.4]),
    }
    bounds = SimpleNamespace(
        income_change=0.3,
        effective_wage_rate_change=0.4,
    )

    income_change = calculate_relative_income_change(measurements, bounds)
    wage_change = calculate_relative_wage_change(measurements, bounds)
    capital_gains_change = calculate_relative_capital_gains_mtr_change(measurements)

    assert np.allclose(income_change, np.array([-0.3, 0.3]))
    assert np.allclose(wage_change, np.array([0.4, -0.25]))
    assert np.allclose(
        capital_gains_change,
        np.array([np.log(0.1) - np.log(0.001), np.log(0.4) - np.log(0.2)]),
    )


def test_lsr_effect_helpers_compute_from_measurements():
    person = FakePerson(simulation=SimpleNamespace())
    person.values.update(
        {
            "employment_income_before_lsr": np.array([50_000.0, -20_000.0]),
            "self_employment_income_before_lsr": np.array([10_000.0, 5_000.0]),
            "sstb_self_employment_income_before_lsr": np.array([20_000.0, 0.0]),
            "income_elasticity": np.array([0.5, 1.0]),
            "substitution_elasticity": np.array([0.2, 0.4]),
        }
    )
    measurements = {
        "baseline_net_income": np.array([100.0, 200.0]),
        "reform_net_income": np.array([110.0, 100.0]),
        "baseline_mtr": np.array([0.2, 1.0]),
        "reform_mtr": np.array([0.1, 0.8]),
        "baseline_capital_gains_mtr": np.array([0.15, 0.2]),
        "reform_capital_gains_mtr": np.array([0.18, 0.22]),
    }
    parameters = make_parameters(
        income_change_bound=0.6,
        wage_change_bound=0.8,
    )

    assert np.allclose(earnings_before_lsr(person, 2026), np.array([80_000.0, 5_000.0]))
    assert np.allclose(
        calculate_income_lsr_effect(person, 2026, parameters, measurements),
        np.array([4_000.0, -2_500.0]),
    )
    assert np.allclose(
        calculate_substitution_lsr_effect(person, 2026, parameters, measurements),
        np.array([2_000.0, 1_600.0]),
    )


def test_earnings_before_lsr_uses_sstb_loss_magnitude():
    person = FakePerson(simulation=SimpleNamespace())
    person.values.update(
        {
            "employment_income_before_lsr": np.array([30_000.0, 0.0]),
            "self_employment_income_before_lsr": np.array([0.0, 0.0]),
            "sstb_self_employment_income_before_lsr": np.array([-20_000.0, -10_000.0]),
        }
    )

    assert np.allclose(
        earnings_before_lsr(person, 2026), np.array([50_000.0, 10_000.0])
    )


def test_behavioral_response_inputs_split_self_employment_between_buckets():
    person = FakePerson(simulation=SimpleNamespace())
    person.values.update(
        {
            "labor_supply_behavioral_response": np.array([1_000.0, 1_000.0]),
            "employment_income_behavioral_response": np.array([0.0, 400.0]),
            "self_employment_income_before_lsr": np.array([0.0, 10_000.0]),
            "sstb_self_employment_income_before_lsr": np.array([20_000.0, 30_000.0]),
        }
    )

    assert np.allclose(
        self_employment_response_module.self_employment_income_behavioral_response.formula(
            person, 2026, None
        ),
        np.array([0.0, 150.0]),
    )
    assert np.allclose(
        sstb_self_employment_response_module.sstb_self_employment_income_behavioral_response.formula(
            person, 2026, None
        ),
        np.array([1_000.0, 450.0]),
    )


def test_behavioral_response_inputs_preserve_sstb_loss_bucket():
    person = FakePerson(simulation=SimpleNamespace())
    person.values.update(
        {
            "labor_supply_behavioral_response": np.array([1_000.0]),
            "employment_income_behavioral_response": np.array([0.0]),
            "self_employment_income_before_lsr": np.array([0.0]),
            "sstb_self_employment_income_before_lsr": np.array([-10_000.0]),
        }
    )

    assert np.allclose(
        self_employment_response_module.self_employment_income_behavioral_response.formula(
            person, 2026, None
        ),
        np.array([0.0]),
    )
    assert np.allclose(
        sstb_self_employment_response_module.sstb_self_employment_income_behavioral_response.formula(
            person, 2026, None
        ),
        np.array([1_000.0]),
    )


def test_lsr_effect_helpers_load_measurements_when_not_provided(monkeypatch):
    person = FakePerson(simulation=SimpleNamespace())
    person.values.update(
        {
            "income_elasticity": np.array([1.0, 2.0]),
            "substitution_elasticity": np.array([3.0, 4.0]),
        }
    )
    measurements = {
        "baseline_net_income": np.array([100.0, 100.0]),
        "reform_net_income": np.array([110.0, 90.0]),
        "baseline_mtr": np.array([0.4, 0.5]),
        "reform_mtr": np.array([0.3, 0.4]),
        "baseline_capital_gains_mtr": np.array([0.1, 0.2]),
        "reform_capital_gains_mtr": np.array([0.2, 0.3]),
    }
    monkeypatch.setattr(
        "policyengine_us.variables.gov.simulation.behavioral_response_measurements.get_behavioral_response_measurements",
        lambda person, period: measurements,
    )
    parameters = make_parameters(
        income_change_bound=0.5,
        wage_change_bound=0.5,
    )

    income_effect = calculate_income_lsr_effect(person, 2026, parameters)
    substitution_effect = calculate_substitution_lsr_effect(person, 2026, parameters)

    assert np.allclose(income_effect, np.array([5_000.0, -5_000.0]))
    assert np.allclose(substitution_effect, np.array([25_000.0, 20_000.0]))


def test_lsr_wrapper_variables_delegate_to_shared_helpers(monkeypatch):
    person = FakePerson(simulation=SimpleNamespace())
    parameters = make_parameters()
    monkeypatch.setattr(
        income_lsr_module,
        "calculate_income_lsr_effect",
        lambda person, period, parameters: np.array([1.0, 2.0]),
    )
    monkeypatch.setattr(
        substitution_lsr_module,
        "calculate_substitution_lsr_effect",
        lambda person, period, parameters: np.array([3.0, 4.0]),
    )

    assert np.array_equal(
        income_elasticity_lsr.formula(person, 2026, parameters),
        np.array([1.0, 2.0]),
    )
    assert np.array_equal(
        substitution_elasticity_lsr.formula(person, 2026, parameters),
        np.array([3.0, 4.0]),
    )


def test_labor_supply_behavioral_response_formula_covers_guards_and_success(
    monkeypatch,
):
    parameters = make_parameters()
    person = FakePerson(simulation=SimpleNamespace(baseline=None))
    assert labor_supply_behavioral_response.formula(person, 2026, parameters) == 0

    person.simulation.baseline = object()
    zero_parameters = make_parameters(
        lsr_income_elasticity=0.0,
        lsr_substitution_elasticity=0.0,
    )
    assert labor_supply_behavioral_response.formula(person, 2026, zero_parameters) == 0

    person.simulation._lsr_calculating = True
    assert labor_supply_behavioral_response.formula(person, 2026, parameters) == 0
    person.simulation._lsr_calculating = False

    monkeypatch.setattr(
        labor_supply_module,
        "get_behavioral_response_measurements",
        lambda person, period: {"placeholder": True},
    )
    monkeypatch.setattr(
        labor_supply_module,
        "calculate_income_lsr_effect",
        lambda person, period, parameters, measurements: np.array([1.0, 2.0]),
    )
    monkeypatch.setattr(
        labor_supply_module,
        "calculate_substitution_lsr_effect",
        lambda person, period, parameters, measurements: np.array([3.0, 4.0]),
    )

    assert np.array_equal(
        labor_supply_behavioral_response.formula(person, 2026, parameters),
        np.array([4.0, 6.0]),
    )
    assert person.simulation._lsr_calculating is False


def test_capital_gains_response_returns_zero_without_baseline_or_elasticity():
    person = FakePerson(simulation=SimpleNamespace(baseline=None))
    parameters = make_parameters(capital_gains_elasticity=-0.62)
    assert capital_gains_behavioral_response.formula(person, 2026, parameters) == 0

    person.simulation.baseline = object()
    zero_elasticity_parameters = make_parameters(capital_gains_elasticity=0.0)
    assert (
        capital_gains_behavioral_response.formula(
            person, 2026, zero_elasticity_parameters
        )
        == 0
    )


def test_capital_gains_elasticity_and_adult_index_formulas():
    person = FakePerson(simulation=SimpleNamespace())
    person.household = object()
    person.values.update(
        {
            "is_adult": np.array([True, True]),
            "long_term_capital_gains_before_response": np.array([1_000.0, 500.0]),
        }
    )
    person.get_rank = lambda household, values, condition=None: np.array([0, 1])
    parameters = make_parameters(capital_gains_elasticity=-0.7)

    assert capital_gains_elasticity.formula(person, 2026, parameters) == -0.7
    assert np.array_equal(adult_index_cg.formula(person, 2026, parameters), [1, 2])


def test_capital_gains_response_and_relative_mtr_change_use_shared_measurements(
    monkeypatch,
):
    measurements = {
        "baseline_capital_gains_mtr": np.array([0.2, 0.4]),
        "reform_capital_gains_mtr": np.array([0.4, 0.2]),
    }
    person = FakePerson(simulation=SimpleNamespace(baseline=object()))
    person.values.update(
        {
            "long_term_capital_gains_before_response": np.array([100.0, 200.0]),
            "capital_gains_elasticity": np.array([-1.0, -1.0]),
        }
    )
    monkeypatch.setattr(
        capital_gains_module,
        "get_behavioral_response_measurements",
        lambda person, period: measurements,
    )
    parameters = make_parameters(capital_gains_elasticity=-1.0)

    relative_change = relative_capital_gains_mtr_change.formula(
        person, 2026, parameters
    )
    response = capital_gains_behavioral_response.formula(person, 2026, parameters)

    assert np.allclose(relative_change, np.array([np.log(2.0), np.log(0.5)]))
    assert np.allclose(response, np.array([-50.0, 200.0]))
