from policyengine_us.model_api import *


class divorce_year(Variable):
    value_type = int
    entity = Person
    label = "The year that the person was divorced."
    definition_period = YEAR
    default_value = 2010
