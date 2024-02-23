from policyengine_us.model_api import *


class adopted_this_year(Variable):
    value_type = bool
    entity = Person
    label = "Person was adopted this year"
    definition_period = YEAR
