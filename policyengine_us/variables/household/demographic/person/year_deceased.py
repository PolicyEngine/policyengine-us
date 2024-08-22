from policyengine_us.model_api import *


class year_deceased(Variable):
    value_type = int
    entity = Person
    label = "Year in which the person deceased"
    definition_period = YEAR
