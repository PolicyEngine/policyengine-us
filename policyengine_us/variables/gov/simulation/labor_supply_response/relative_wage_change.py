from policyengine_us.model_api import *


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
        p = parameters(period).gov.simulation.labor_supply_responses
        return np.clip(
            relative_change,
            -p.bounds.effective_wage_rate_change,
            p.bounds.effective_wage_rate_change,
        )
