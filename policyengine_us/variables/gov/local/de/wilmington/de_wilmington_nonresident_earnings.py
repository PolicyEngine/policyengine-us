from policyengine_us.model_api import *


class de_wilmington_nonresident_earnings(Variable):
    value_type = float
    entity = Person
    label = "Wilmington-source earnings of a nonresident"
    unit = USD
    definition_period = YEAR
