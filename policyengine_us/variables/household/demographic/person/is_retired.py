from policyengine_us.model_api import *


class is_retired(Variable):
    value_type = bool
    entity = Person
    label = "Is retired"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Conventional assumption that retirement begins at age 65.
        return person("age", period) >= 65
