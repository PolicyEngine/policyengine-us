from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    user_set_variables,
)
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_relative_capital_gains_mtr_change,
    get_behavioral_response_measurements,
)


class relative_capital_gains_mtr_change(Variable):
    value_type = float
    entity = Person
    label = "relative change in capital gains tax rate"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):  # pragma: no cover
        measurements = get_behavioral_response_measurements(person, period)
        return calculate_relative_capital_gains_mtr_change(measurements)


class capital_gains_elasticity(Variable):
    value_type = float
    entity = Person
    label = "elasticity of capital gains realizations"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        gov = parameters(period).gov
        return gov.simulation.capital_gains_responses.elasticity


class capital_gains_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "capital gains behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        simulation = person.simulation
        if simulation.baseline is None:
            return 0

        if parameters(period).gov.simulation.capital_gains_responses.elasticity == 0:
            return 0

        capital_gains = person("long_term_capital_gains_before_response", period)
        measurements = get_behavioral_response_measurements(person, period)
        tax_rate_change = calculate_relative_capital_gains_mtr_change(measurements)
        elasticity = person("capital_gains_elasticity", period)

        # Calculate response using log differences
        response_factor = np.exp(elasticity * tax_rate_change) - 1
        response = capital_gains * response_factor

        return response


class long_term_capital_gains_before_response(Variable):
    label = "capital gains before responses"
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = USD
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"


class adult_index_cg(Variable):
    value_type = int
    entity = Person
    label = "index of adult in household, ranked by capital gains"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person.get_rank(
                person.household,
                -person("long_term_capital_gains_before_response", period),
                condition=person("is_adult", period),
            )
            + 1
        )


# marginal_tax_rate_on_capital_gains raises long-term gains by at least $1,000.
# The rate is a difference in household_net_income, a float32 that resolves
# only about 1.2e-7 of its own size (8 dollars at $100 million), so a fixed
# $1,000 rise would resolve a $100 million household's rate only to 0.008.
# The rise is therefore 0.1% of the larger of the household's net income and
# the person's long-term gains, in absolute value, where that exceeds $1,000,
# which keeps the resolution near 1e-4. Below $1 million both give $1,000.
CAPITAL_GAINS_MTR_MINIMUM_RISE = 1_000
CAPITAL_GAINS_MTR_RELATIVE_RISE = 1e-3


def capital_gains_mtr_rise(household_net_income, long_term_capital_gains):
    """Rise in long-term gains that measures each person's rate."""
    scale = np.maximum(
        np.abs(np.asarray(household_net_income, dtype=np.float64)),
        np.abs(np.asarray(long_term_capital_gains, dtype=np.float64)),
    )
    return np.maximum(
        CAPITAL_GAINS_MTR_MINIMUM_RISE, CAPITAL_GAINS_MTR_RELATIVE_RISE * scale
    )


class marginal_tax_rate_on_capital_gains(Variable):
    label = "capital gains marginal tax rate"
    documentation = (
        "Share of a rise in long-term capital gains that does not increase"
        " household net income. The rise is $1,000, or 0.1% of the household's"
        " net income or of the person's long-term gains where that is more."
        " Simulated only for the two adults in each household with the largest"
        " long-term capital gains (adult_index_cg 1 and 2), regardless of"
        " simulation.marginal_tax_rate_adults; zero for everyone else."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):  # pragma: no cover
        # Requires simulation branching - tested via household simulations
        # in tests/core/test_capital_gains_mtr_measurement.py
        mtr_values = np.zeros(person.count, dtype=np.float32)
        simulation = person.simulation
        adult_index_values = person("adult_index_cg", period)
        long_term_capital_gains = person("long_term_capital_gains", period)
        household_net_income = person.household("household_net_income", period)
        rise = capital_gains_mtr_rise(household_net_income, long_term_capital_gains)
        inputs = user_set_variables(simulation)
        for adult_index in [1, 2]:
            alt_simulation = simulation.get_branch(f"adult_{adult_index}_cg_rise")
            mask = adult_index_values == adult_index
            for variable in simulation.tax_benefit_system.variables:
                variable_data = simulation.tax_benefit_system.variables[variable]
                if variable not in inputs and not variable_data.is_input_variable():
                    alt_simulation.delete_arrays(variable)
            # Raise long-term gains, which net capital gain and so the
            # preferential rates read. Raising capital_gains, the sum of
            # short- and long-term gains, reached adjusted gross income but
            # not net capital gain, so the rise was taxed as ordinary income.
            # The override holds any behavioral response at its value here.
            alt_simulation.set_input(
                "long_term_capital_gains",
                period,
                long_term_capital_gains + mask * rise,
            )
            alt_person = alt_simulation.person
            # Divide by the rise as stored, after rounding to float32.
            stored_rise = (
                alt_person("long_term_capital_gains", period) - long_term_capital_gains
            )
            household_net_income_higher_gains = alt_person.household(
                "household_net_income", period
            )
            increase = household_net_income_higher_gains - household_net_income
            mtr_values += where(mask, 1 - increase / where(mask, stored_rise, 1), 0)

            del simulation.branches[f"adult_{adult_index}_cg_rise"]
        return mtr_values
