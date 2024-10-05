from policyengine_us.model_api import *


class birth_year(Variable):
    value_type = int
    entity = Person
    label = "Birth year"
    unit = "year"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        return period.start.year - age
