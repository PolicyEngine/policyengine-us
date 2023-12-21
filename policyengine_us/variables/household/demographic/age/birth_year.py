from policyengine_us.model_api import *


class age(Variable):
    value_type = float
    entity = Person
    label = "age"
    definition_period = YEAR
    default_value = 40

    def formula(person, period, parameters):
        age = person("age", period)
        return -(age - period.start.year)
