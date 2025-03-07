from policyengine_us.model_api import *


class pregnancy_weeks(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = "FISC Act family income supplement pregnancy weeks limit"
