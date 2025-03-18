from policyengine_us.model_api import *
from policyengine_core.simulations import *


class relative_capital_gains_mtr_change(Variable):
    value_type = float
    entity = Person
    label = "relative change in capital gains tax rate"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        simulation: Simulation = person.simulation
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_cgr_measurement", clone_system=True
        )
        baseline_person = baseline_branch.populations["person"]
        baseline_branch.tax_benefit_system.neutralize_variable(
            "capital_gains_behavioral_response"
        )
        baseline_branch.set_input(
            "long_term_capital_gains_before_response",
            period,
            person("long_term_capital_gains_before_response", period),
        )
        baseline_mtr = baseline_person(
            "marginal_tax_rate_on_capital_gains", period
        )
        del simulation.branches["baseline"].branches[
            "baseline_cgr_measurement"
        ]

        measurement_branch = simulation.get_branch(
            "cgr_measurement", clone_system=True
        )
        measurement_branch.tax_benefit_system.neutralize_variable(
            "capital_gains_behavioral_response"
        )
        measurement_branch.set_input(
            "long_term_capital_gains_before_response",
            period,
            person("long_term_capital_gains_before_response", period),
        )
        measurement_person = measurement_branch.populations["person"]
        reform_mtr = measurement_person(
            "marginal_tax_rate_on_capital_gains", period
        )
        del simulation.branches["cgr_measurement"]

        # Handle zeros in tax rates to prevent log(0)
        min_rate = 0.001
        baseline_mtr_adj = np.maximum(baseline_mtr, min_rate)
        reform_mtr_adj = np.maximum(reform_mtr, min_rate)

        # Calculate log difference
        return np.log(reform_mtr_adj) - np.log(baseline_mtr_adj)


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

        if (
            parameters(
                period
            ).gov.simulation.capital_gains_responses.elasticity
            == 0
        ):
            return 0

        capital_gains = person(
            "long_term_capital_gains_before_response", period
        )
        tax_rate_change = person("relative_capital_gains_mtr_change", period)
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
    documentation = "Percent of marginal capital gains that do not increase household net income."
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        mtr_values = np.zeros(person.count, dtype=np.float32)
        simulation = person.simulation
        DELTA = 1_000
        adult_index_values = person("adult_index_cg", period)
        for adult_index in [1, 2]:
            alt_simulation = simulation.get_branch(
                f"adult_{adult_index}_cg_rise"
            )
            mask = adult_index_values == adult_index
            for variable in simulation.tax_benefit_system.variables:
                variable_data = simulation.tax_benefit_system.variables[
                    variable
                ]
                if (
                    variable not in simulation.input_variables
                    and not variable_data.is_input_variable()
                ):
                    alt_simulation.delete_arrays(variable)
            alt_simulation.set_input(
                "capital_gains",
                period,
                person("capital_gains", period) + mask * DELTA,
            )
            alt_person = alt_simulation.person
            household_net_income = person.household(
                "household_net_income", period
            )
            household_net_income_higher_earnings = alt_person.household(
                "household_net_income", period
            )
            increase = (
                household_net_income_higher_earnings - household_net_income
            )
            mtr_values += where(mask, 1 - increase / DELTA, 0)

            del simulation.branches[f"adult_{adult_index}_cg_rise"]
        return mtr_values
