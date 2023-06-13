from policyengine_us.model_api import *


class co_chp_urgent_care_saving(Variable):
    value_type = float
    entity = Person
    label = "Child Health Plan Plus urgent care expense reduction"
    definition_period = YEAR

    def formula(person, period, parameters):
        income_level = person("medicaid_income_level", period)
        copay = parameters(
            period
        ).gov.states.co.hcpf.chp.copays.urgent_care.calc(income_level)
        expense = person("urgent_care_expense")
        return max_(0, expense - copay)
