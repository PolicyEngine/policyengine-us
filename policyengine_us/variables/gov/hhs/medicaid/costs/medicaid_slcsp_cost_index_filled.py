from policyengine_us.model_api import *


class medicaid_slcsp_cost_index_filled(Variable):
    value_type = float
    entity = Person
    label = "Medicaid SLCSP cost index with state fallback"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        cost_index = person("medicaid_slcsp_cost_index", period)
        state_average = person("medicaid_slcsp_state_average_cost_index", period)
        return where(cost_index > 0, cost_index, state_average)
