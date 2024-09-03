from policyengine_us.model_api import *


class divorce_year(Variable):
    value_type = int
    entity = Person
    label = "The year that the Person was divorced"
    definition_period = YEAR
    defined_for = "is_divorced"
    default_value = 2010
