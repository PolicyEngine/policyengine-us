from policyengine_us.model_api import *


class year_of_retirement(Variable):
    value_type = int
    entity = Person
    label = "Year of retirement"
    definition_period = YEAR
