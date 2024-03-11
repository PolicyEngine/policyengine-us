from policyengine_us.model_api import *


class keogh_distributions(Variable):
    value_type = float
    entity = Person
    label = "KEOGH distributions"
    unit = USD
    definition_period = YEAR
