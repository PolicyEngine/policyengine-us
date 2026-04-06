from policyengine_us.model_api import *

BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH = "behavioral_response_measurement"
BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH = (
    "baseline_behavioral_response_measurement"
)
BEHAVIORAL_RESPONSE_CACHE_ATTR = "_behavioral_response_measurements"
NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES = (
    "employment_income_behavioral_response",
    "self_employment_income_behavioral_response",
    "capital_gains_behavioral_response",
)
BEHAVIORAL_RESPONSE_INPUT_VARIABLES = (
    "employment_income_before_lsr",
    "self_employment_income_before_lsr",
    "long_term_capital_gains_before_response",
)


def _neutralize_behavioral_responses(branch):
    for variable in NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES:
        branch.tax_benefit_system.neutralize_variable(variable)


def _copy_behavioral_response_inputs(branch, person, period):
    for variable in BEHAVIORAL_RESPONSE_INPUT_VARIABLES:
        branch.set_input(variable, period, person(variable, period))


def _behavioral_response_cache(simulation):
    cache = getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR, None)
    if cache is None:
        cache = {}
        setattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR, cache)
    return cache


def get_behavioral_response_measurements(person, period):  # pragma: no cover
    # Requires reform scenario with simulation branching - tested via microsim
    simulation = person.simulation
    cache = _behavioral_response_cache(simulation)
    period_key = str(period)

    if period_key in cache:
        return cache[period_key]

    measurement_branch = simulation.get_branch(
        BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, clone_system=True
    )
    baseline_parent = simulation.get_branch("baseline")
    baseline_branch = baseline_parent.get_branch(
        BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, clone_system=True
    )
    baseline_branch.tax_benefit_system.parameters.simulation = (
        measurement_branch.tax_benefit_system.parameters.simulation
    )

    try:
        for branch in (measurement_branch, baseline_branch):
            _neutralize_behavioral_responses(branch)
            _copy_behavioral_response_inputs(branch, person, period)

        measurement_person = measurement_branch.populations["person"]
        baseline_person = baseline_branch.populations["person"]
        measurements = {
            "baseline_net_income": baseline_person.household(
                "household_net_income", period
            ),
            "reform_net_income": measurement_person.household(
                "household_net_income", period
            ),
            "baseline_mtr": baseline_person("marginal_tax_rate", period),
            "reform_mtr": measurement_person("marginal_tax_rate", period),
            "baseline_capital_gains_mtr": baseline_person(
                "marginal_tax_rate_on_capital_gains", period
            ),
            "reform_capital_gains_mtr": measurement_person(
                "marginal_tax_rate_on_capital_gains", period
            ),
        }
        cache[period_key] = measurements
        simulation.macro_cache_read = False
        simulation.macro_cache_write = False
        return measurements
    finally:
        baseline_parent.branches.pop(
            BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, None
        )
        simulation.branches.pop(BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, None)


def earnings_before_lsr(person, period):
    raw_earnings = add(
        person,
        period,
        [
            "employment_income_before_lsr",
            "self_employment_income_before_lsr",
        ],
    )
    return max_(raw_earnings, 0)


def calculate_relative_income_change(measurements, bounds):
    baseline_net_income = measurements["baseline_net_income"]
    reform_net_income = measurements["reform_net_income"]
    baseline_net_income_c = np.clip(baseline_net_income, 1, None)
    reform_net_income_c = np.clip(reform_net_income, 1, None)
    relative_change = (
        reform_net_income_c - baseline_net_income_c
    ) / baseline_net_income_c
    return np.clip(relative_change, -bounds.income_change, bounds.income_change)


def calculate_relative_wage_change(measurements, bounds):
    baseline_wage = 1 - measurements["baseline_mtr"]
    reform_wage = 1 - measurements["reform_mtr"]
    baseline_wage_c = np.where(baseline_wage == 0, 0.01, baseline_wage)
    reform_wage_c = np.where(reform_wage == 0, 0.01, reform_wage)
    relative_change = (reform_wage_c - baseline_wage_c) / baseline_wage_c
    return np.clip(
        relative_change,
        -bounds.effective_wage_rate_change,
        bounds.effective_wage_rate_change,
    )


def calculate_relative_capital_gains_mtr_change(measurements):
    min_rate = 0.001
    baseline_mtr = np.maximum(measurements["baseline_capital_gains_mtr"], min_rate)
    reform_mtr = np.maximum(measurements["reform_capital_gains_mtr"], min_rate)
    return np.log(reform_mtr) - np.log(baseline_mtr)


def calculate_income_lsr_effect(person, period, parameters, measurements=None):
    if measurements is None:
        measurements = get_behavioral_response_measurements(person, period)
    lsr_parameters = parameters(period).gov.simulation.labor_supply_responses
    return (
        earnings_before_lsr(person, period)
        * calculate_relative_income_change(measurements, lsr_parameters.bounds)
        * person("income_elasticity", period)
    )


def calculate_substitution_lsr_effect(person, period, parameters, measurements=None):
    if measurements is None:
        measurements = get_behavioral_response_measurements(person, period)
    lsr_parameters = parameters(period).gov.simulation.labor_supply_responses
    return (
        earnings_before_lsr(person, period)
        * calculate_relative_wage_change(measurements, lsr_parameters.bounds)
        * person("substitution_elasticity", period)
    )
