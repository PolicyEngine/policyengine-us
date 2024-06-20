from policyengine_us.model_api import *


class year_deceased(Variable):
    value_type = int
    entity = Person
    label = "Year deceased"
    definition_period = YEAR
