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
        p = parameters(period).gov.simulation.labor_supply_responses
        # _c suffix for "clipped"
        baseline_net_income_c = np.clip(baseline_net_income, 1, None)
        net_income_c = np.clip(net_income, 1, None)
        relative_change = (
            net_income_c - baseline_net_income_c
        ) / baseline_net_income_c
        return np.clip(
            relative_change, -p.bounds.income_change, p.bounds.income_change
        )
