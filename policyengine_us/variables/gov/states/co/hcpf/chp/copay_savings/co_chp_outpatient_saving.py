from policyengine_us.model_api import *


class co_chp_outpatient_saving(Variable):
    value_type = float
    entity = Person
    label = "Child Health Plan Plus outpatient expense reduction"
    definition_period = YEAR

    def formula(person, period, parameters):
        income_level = person("medicaid_income_level", period)
        copay = parameters(
            period
        ).gov.states.co.hcpf.chp.copays.outpatient.calc(income_level)
        expense = person("outpatient_expense")
        return max_(0, expense - copay)
