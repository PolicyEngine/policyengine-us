from policyengine_us.model_api import *


class sep_distributions(Variable):
    value_type = float
    entity = Person
    label = "SEP distributions"
    unit = USD
    definition_period = YEAR
