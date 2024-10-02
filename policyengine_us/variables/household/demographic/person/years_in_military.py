from policyengine_us.model_api import *


class years_in_military(Variable):
    value_type = int
    entity = Person
    label = "Years served in military"
    definition_period = YEAR
