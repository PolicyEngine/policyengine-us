from policyengine_us.model_api import *


class relative_income_change(Variable):
    value_type = float
    entity = Person
    label = "relative income change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_response"

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
        baseline_net_income_c = np.where(
            baseline_net_income == 0, 1, baseline_net_income
        )
        net_income_c = np.where(net_income == 0, 1, net_income)
        relative_change = (
            net_income_c - baseline_net_income_c
        ) / baseline_net_income_c
        return np.clip(relative_change, -1, 1)


class relative_wage_change(Variable):
    value_type = float
    entity = Person
    label = "relative wage change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_response"

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
        wage = 1 - mtr
        baseline_wage_c = np.where(baseline_wage == 0, 1, baseline_wage)
        wage_c = np.where(wage == 0, 1, wage)
        relative_change = (wage_c - baseline_wage_c) / baseline_wage_c
        return np.clip(relative_change, -1, 1)


class income_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply response"
    unit = USD
    definition_period = YEAR
    requires_computation_after = "labor_supply_response"

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
    requires_computation_after = "labor_supply_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        wage_change = person("relative_wage_change", period)

        return employment_income * wage_change * lsr.substitution_elasticity


class labor_supply_response(Variable):
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
                "labor_supply_response"
            )

        return person("income_elasticity_lsr", period) + person(
            "substitution_elasticity_lsr", period
        )
