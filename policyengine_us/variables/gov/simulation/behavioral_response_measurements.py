from policyengine_us.model_api import *
from policyengine_us.spm import BEHAVIORAL_RESPONSE_CACHE_ATTR, clone_spm_system
from policyengine_us.tools.period_branch import drop_inherited_values

BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH = "behavioral_response_measurement"
BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH = (
    "baseline_behavioral_response_measurement"
)
NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES = (
    "employment_income_behavioral_response",
    "self_employment_income_behavioral_response",
    "sstb_self_employment_income_behavioral_response",
    "capital_gains_behavioral_response",
)
BEHAVIORAL_RESPONSE_INPUT_VARIABLES = (
    "employment_income_before_lsr",
    "self_employment_income_before_lsr",
    "sstb_self_employment_income_before_lsr",
    "long_term_capital_gains_before_response",
)


def _neutralize_behavioral_responses(branch):
    for variable in NEUTRALIZED_BEHAVIORAL_RESPONSE_VARIABLES:
        branch.tax_benefit_system.neutralize_variable(variable)


def _copy_behavioral_response_inputs(branch, person, period):
    for variable in BEHAVIORAL_RESPONSE_INPUT_VARIABLES:
        branch.set_input(variable, period, person(variable, period))


def _behavioral_response_cache(simulation):
    """This simulation's measurements, by period.

    Each simulation has its own dictionary: ``SPMSimulationMixin`` gives a
    clone an empty one and a branch a copy of its parent's, and drops it with
    the rest of the cached formula output (``_invalidate_all_caches``).
    """
    cache = simulation.__dict__.get(BEHAVIORAL_RESPONSE_CACHE_ATTR)
    if cache is None:
        cache = {}
        simulation.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR] = cache
    return cache


def _baseline_measurement_branch(simulation):
    """Branch ``simulation`` under baseline policy, keeping only its inputs.

    The baseline measurement applies baseline policy to the inputs of the
    simulation being measured, as the reform measurement applies the
    simulation's own policy to them. ``simulation.baseline`` has the baseline
    policy, but its inputs need not be the simulation's:

    - A branch shares its parent's baseline, and on policyengine-core before
      #587 so does a clone, so their baseline holds the parent's inputs.
    - A reform simulation's baseline is a branch taken while it was built,
      before this package moved ``employment_income`` and the other
      pre-response inputs to their ``_before_lsr`` variables, so a household
      baseline keeps them as overrides; later inputs never reach it.

    ``simulation.get_branch("baseline")``, used before, was worse: for a branch
    or an early clone it made a new branch under the *reform* policy, so the
    response was measured against the reform itself and came out zero.

    So branch the simulation itself and give the branch a private copy of the
    baseline policy, as core does for a reform simulation's own baseline. Then
    drop every array the branch copied except inputs: the rest was calculated
    under the reform. Like that baseline, the branch has no baseline of its own,
    so its behavioural responses are zero.
    """
    branch = simulation.get_branch(BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH)
    branch.tax_benefit_system = clone_spm_system(simulation.baseline.tax_benefit_system)
    branch.baseline = None
    branch._rebind_holders()
    drop_inherited_values(branch)
    branch._isolate_parameter_tracing()
    # The policy copy's receipts list the counties the baseline read; record
    # the ones this branch reads, which are the simulation's.
    branch._record_own_county_input_types()
    return branch


def get_behavioral_response_measurements(person, period):  # pragma: no cover
    # Requires reform scenario with simulation branching - tested via microsim
    simulation = person.simulation
    cache = _behavioral_response_cache(simulation)
    period_key = str(period)

    if period_key in cache:
        return cache[period_key]

    try:
        measurement_branch = simulation.get_branch(
            BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, clone_system=True
        )
        baseline_branch = _baseline_measurement_branch(simulation)
        baseline_branch.tax_benefit_system.parameters.simulation = (
            measurement_branch.tax_benefit_system.parameters.simulation
        )
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
        simulation.branches.pop(BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, None)
        simulation.branches.pop(BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, None)


def earnings_before_lsr(person, period):
    employment_income = max_(person("employment_income_before_lsr", period), 0)
    self_employment_income = abs(person("self_employment_income_before_lsr", period))
    sstb_self_employment_income = abs(
        person("sstb_self_employment_income_before_lsr", period)
    )
    return employment_income + self_employment_income + sstb_self_employment_income


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
