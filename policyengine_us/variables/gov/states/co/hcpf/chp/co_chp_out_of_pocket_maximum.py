from policyengine_us.model_api import *


class co_chp_out_of_pocket_maximum(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Health Plan Plus out of pocket maximum"
    definition_period = YEAR

    def formula(person, period, parameters):
        income = person.tax_unit("medicaid_income", period)
        percent = parameters(period).gov.states.co.hcpf.chp.out_of_pocket
        return income * percent
