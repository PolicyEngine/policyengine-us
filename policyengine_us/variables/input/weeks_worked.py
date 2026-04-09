from policyengine_us.model_api import *


class weeks_worked(Variable):
    value_type = int
    entity = Person
    label = "Weeks worked during the year"
    definition_period = YEAR
    documentation = "Number of weeks worked during the year."

    def formula_2025(person, period, parameters):
        return person("weeks_worked", period.last_year)
