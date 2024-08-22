from policyengine_us.model_api import *


class co_chp(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Health Plan Plus expense savings"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        saving = 0
        income_level = person("medicaid_income_level", period)
        is_pregnant = person("is_pregnant", period)
        p = parameters(period).gov.states.co.hcpf.chp
        elements = p.expenses
        for element in elements:
            copay = ~is_pregnant * p.copays[element].calc(income_level)
            expense = person(element + "_expense", period)
            saving += max_(0, expense - copay)
        return saving
