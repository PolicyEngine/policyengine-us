from policyengine_us.model_api import *


class co_chp_out_of_pocket_maximum(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Health Plan Plus out of pocket maximum"
    definition_period = YEAR

    def formula(person, period, parameters):
        income_level = person("medicaid_income_level", period)
        percent = parameters(period).gov.states.co.hcpf.chp.out_of_pocket
        return income_level * percent
