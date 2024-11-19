from policyengine_us.model_api import *


class monthly_age(Variable):
    value_type = float
    entity = Person
    label = "Monthly age"
    definition_period = MONTH

    def formula(person, period, parameters):
        yearly_age = person("age", period)
        return yearly_age * MONTHS_IN_YEAR
