from policyengine_us.model_api import *


class mt_old_age_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Montana old age subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.old_age
        # Aged taxpayers are eligible for a subtraction amount
        age = person("age", period)
        return p.amount.calc(age)
