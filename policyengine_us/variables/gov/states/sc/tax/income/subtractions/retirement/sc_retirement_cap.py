from policyengine_us.model_api import *


class sc_retirement_cap(Variable):
    value_type = float
    entity = Person
    label = "South Carolina retirement income subtraction cap"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        age = person("age", period)
        return p.cap.calc(age)
