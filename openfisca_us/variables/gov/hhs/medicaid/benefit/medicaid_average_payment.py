from openfisca_us.model_api import *


class medicaid_average_payment(Variable):
    value_type = float
    entity = Person
    label = "Average Medicaid payment for this person's State"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        calibration = parameters(period).calibration
        return (
            calibration.programs.medicaid.budgetary_impact[state_code]
            / calibration.populations.by_state[state_code]
        )
