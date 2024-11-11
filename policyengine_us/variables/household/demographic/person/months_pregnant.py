from policyengine_us.model_api import *


class months_pregnant(Variable):
    value_type = int
    entity = Person
    label = "Number of months into the pregnancy"
    definition_period = YEAR
