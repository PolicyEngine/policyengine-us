from policyengine_us.model_api import *


class relative_income_change(Variable):
    value_type = float
    entity = Person
    label = "relative income change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        simulation = person.simulation
        measurement_branch = simulation.get_branch("lsr_measurement")
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement"
        )
        baseline_person = baseline_branch.populations["person"]
        baseline_net_income = baseline_person.household(
            "household_net_income", period
        )
        measurement_person = measurement_branch.populations["person"]
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
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        simulation = person.simulation
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement"
        )
        baseline_person = baseline_branch.populations["person"]
        baseline_mtr = baseline_person("marginal_tax_rate", period)
        baseline_wage = 1 - baseline_mtr
        measurement_branch = simulation.get_branch("lsr_measurement")
        measurement_person = measurement_branch.populations["person"]
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
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = employment_income + self_employment_income
        income_change = person("relative_income_change", period)
        return earnings * income_change * person("income_elasticity", period)


class income_elasticity(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR
    adds = ["gov.simulation.labor_supply_responses.elasticities.income"]


class substitution_elasticity(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        gov = parameters(period).gov
        elasticities_p = (
            gov.simulation.labor_supply_responses.elasticities.substitution
        )

        if elasticities_p.all != 0:
            return elasticities_p.all

        earnings_decile_markers = [  # Parametrise
            0,
            14e3,
            28e3,
            39e3,
            50e3,
            61e3,
            76e3,
            97e3,
            138e3,
            1_726e3,
        ]

        earnings = person("employment_income_before_lsr", period) + person(
            "self_employment_income_before_lsr", period
        )
        earnings_decile = (
            np.searchsorted(earnings_decile_markers, earnings) + 1
        )

        tax_unit_earnings = person.tax_unit.sum(earnings)
        # Primary earner == highest earner in tax unit
        is_primary_earner = tax_unit_earnings == person.tax_unit.max(earnings)

        elasticities = np.zeros_like(earnings)

        p = elasticities_p.by_position_and_decile
        elasticities[~is_primary_earner] = p.secondary
        decile_elasticities = [
            p.primary._children[str(i + 1)] for i in range(10)
        ]
        for i in range(10):
            elasticities[earnings_decile == i + 1] = decile_elasticities[i]

        return elasticities


class substitution_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply response"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = employment_income + self_employment_income
        wage_change = person("relative_wage_change", period)
        return (
            earnings * wage_change * person("substitution_elasticity", period)
        )


class labor_supply_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "earnings-related labor supply change"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        gov = parameters(period).gov
        lsr = gov.simulation.labor_supply_responses
        simulation = person.simulation
        if simulation.baseline is None:
            return 0  # No reform, no impact
        if (
            lsr.elasticities.income == 0
            and lsr.elasticities.substitution.all == 0
        ):
            return 0

        measurement_branch = simulation.get_branch(
            "lsr_measurement", clone_system=True
        )  # A branch without LSRs
        baseline_branch = simulation.get_branch("baseline").get_branch(
            "baseline_lsr_measurement", clone_system=True
        )  # Already created by default
        baseline_branch.tax_benefit_system.parameters.simulation = (
            measurement_branch.tax_benefit_system.parameters.simulation
        )

        # (system with LSRs) <- (system without LSRs used to calculate LSRs)
        #                      |
        #                      * -(baseline system without LSRs used to calculate LSRs)

        for branch in [measurement_branch, baseline_branch]:
            branch.tax_benefit_system.neutralize_variable(
                "employment_income_behavioral_response"
            )
            branch.tax_benefit_system.neutralize_variable(
                "self_employment_income_behavioral_response"
            )
            branch.set_input(
                "employment_income_before_lsr",
                period,
                person("employment_income_before_lsr", period),
            )
            branch.set_input(
                "self_employment_income_before_lsr",
                period,
                person("self_employment_income_before_lsr", period),
            )

        response = add(
            person,
            period,
            [
                "income_elasticity_lsr",
                "substitution_elasticity_lsr",
            ],
        )
        simulation = person.simulation
        del simulation.branches["baseline"].branches[
            "baseline_lsr_measurement"
        ]
        del simulation.branches["lsr_measurement"]

        simulation.macro_cache_read = False
        simulation.macro_cache_write = False

        return response


class employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = employment_income + self_employment_income
        emp_share = np.ones_like(earnings)
        mask = earnings > 0
        emp_share[mask] = employment_income[mask] / earnings[mask]
        return lsr * emp_share


class self_employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "self-employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        emp_response = person("employment_income_behavioral_response", period)

        return lsr - emp_response
