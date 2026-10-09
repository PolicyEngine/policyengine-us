from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_relative_capital_gains_mtr_change,
    get_behavioral_response_measurements,
)
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    create_perturbed_branch,
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


class marginal_tax_rate_on_capital_gains(Variable):
    label = "capital gains marginal tax rate"
    documentation = (
        "Percent of marginal capital gains that do not increase household net income."
        " Simulated only for the two adults in each household with the largest"
        " long-term capital gains (adult_index_cg 1 and 2), regardless of"
        " simulation.marginal_tax_rate_adults; zero for everyone else."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):  # pragma: no cover
        # Requires simulation branching - tested via microsim
        mtr_values = np.zeros(person.count, dtype=np.float32)
        simulation = person.simulation
        DELTA = 1_000
        adult_index_values = person("adult_index_cg", period)
        household_net_income = person.household("household_net_income", period)
        for adult_index in [1, 2]:
            branch_name = f"adult_{adult_index}_cg_rise"
            mask = adult_index_values == adult_index
            # Raise long-term gains, the gains the behavioral response scales,
            # so the preferential rates apply to the increase.
            alt_simulation = create_perturbed_branch(
                simulation,
                period,
                branch_name,
                {"long_term_capital_gains": mask * DELTA},
            )
            household_net_income_higher_gains = alt_simulation.person.household(
                "household_net_income", period
            )
            increase = household_net_income_higher_gains - household_net_income
            mtr_values += where(mask, 1 - increase / DELTA, 0)

            del simulation.branches[branch_name]
        return mtr_values
