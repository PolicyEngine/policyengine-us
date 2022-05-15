from openfisca_us.model_api import *


class medicaid_benefit_value(Variable):
    value_type = float
    entity = Person
    label = "Average Medicaid payment"
    unit = USD
    documentation = "Per-capita payment for this person's State."
    definition_period = YEAR

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        calibration = parameters(period).calibration
        spending = calibration.programs.medicaid.budgetary_impact[state]
        population = calibration.populations.by_state[state]
        return spending / population
