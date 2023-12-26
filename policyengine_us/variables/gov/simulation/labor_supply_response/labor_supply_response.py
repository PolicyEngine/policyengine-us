from policyengine_us.model_api import *


class relative_income_change(Variable):
    value_type = float
    entity = Person
    label = "relative income change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "employment_income_behavioral_response"

    def formula(person, period, parameters):
        simulation = person.simulation
        measurement_branch = simulation.get_branch("lsr_measurement")
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement"
        )
        measurement_person = measurement_branch.populations["person"]
        baseline_person = baseline_branch.populations["person"]
        baseline_net_income = baseline_person.household(
            "household_net_income", period
        )
        net_income = measurement_person.household(
            "household_net_income", period
        )
        income_change_bound = parameters(
            period
        ).gov.simulation.labor_supply_responses.bounds.income_change
        # _c suffix for "clipped"
        baseline_net_income_c = np.clip(baseline_net_income, 1, None)
        net_income_c = np.clip(net_income, 1, None)
        relative_change = (
            net_income_c - baseline_net_income_c
        ) / baseline_net_income_c
        return np.clip(
            relative_change, -income_change_bound, income_change_bound
        )


class relative_wage_change(Variable):
    value_type = float
    entity = Person
    label = "relative wage change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "employment_income_behavioral_response"

    def formula(person, period, parameters):
        simulation = person.simulation
        measurement_branch = simulation.get_branch("lsr_measurement")
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement"
        )
        measurement_person = measurement_branch.populations["person"]
        baseline_person = baseline_branch.populations["person"]
        baseline_mtr = baseline_person("marginal_tax_rate", period)
        baseline_wage = 1 - baseline_mtr
        mtr = measurement_person("marginal_tax_rate", period)
        wage_rate = 1 - mtr
        # _c suffix for "clipped"
        baseline_wage_c = np.where(baseline_wage == 0, 0.01, baseline_wage)
        wage_rate_c = np.where(wage_rate == 0, 0.01, wage_rate)
        relative_change = (wage_rate_c - baseline_wage_c) / baseline_wage_c
        wage_change_bound = parameters(
            period
        ).gov.simulation.labor_supply_responses.bounds.effective_wage_rate_change
        return np.clip(relative_change, -wage_change_bound, wage_change_bound)


class income_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply response"
    unit = USD
    definition_period = YEAR
    requires_computation_after = "employment_income_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        income_change = person("relative_income_change", period)

        return employment_income * income_change * lsr.income_elasticity


class substitution_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply response"
    unit = USD
    definition_period = YEAR
    requires_computation_after = "employment_income_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        wage_change = person("relative_wage_change", period)

        return employment_income * wage_change * lsr.substitution_elasticity


class employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "income-related labor supply change"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        simulation = person.simulation
        if simulation.baseline is None:
            return 0  # No reform, no impact
        if lsr.income_elasticity == 0 and lsr.substitution_elasticity == 0:
            return 0

        measurement_branch = simulation.get_branch(
            "lsr_measurement", clone_system=True
        )  # A branch without LSRs
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement", clone_system=True
        )  # Already created by default

        # (system with LSRs) <- (system without LSRs used to calculate LSRs)
        #                      |
        #                      * -(baseline system without LSRs used to calculate LSRs)

        for branch in [measurement_branch, baseline_branch]:
            branch.tax_benefit_system.neutralize_variable(
                "employment_income_behavioral_response"
            )
            branch.set_input(
                "employment_income_before_lsr",
                period,
                person("employment_income_before_lsr", period),
            )

        return add(
            person,
            period,
            [
                "income_elasticity_lsr",
                "substitution_elasticity_lsr",
            ],
        )
