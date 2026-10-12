from policyengine_us.model_api import *


class ny_yonkers_nonresident_earnings(Variable):
    value_type = float
    entity = Person
    label = "Yonkers-source wages of a nonresident"
    unit = USD
    definition_period = YEAR
