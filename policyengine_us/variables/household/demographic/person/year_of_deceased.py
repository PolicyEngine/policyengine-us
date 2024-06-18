from policyengine_us.model_api import *


class year_of_deceased(Variable):
    value_type = int
    entity = Person
    label = "Year of deceased"
    definition_period = YEAR
