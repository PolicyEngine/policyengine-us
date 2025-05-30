from policyengine_us.model_api import *


class labor_supply_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "earnings-related labor supply change"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.simulation.labor_supply_responses
        simulation = person.simulation
        if simulation.baseline is None:
            return 0  # No reform, no impact
        if p.elasticities.income == 0 and p.elasticities.substitution.all == 0:
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
