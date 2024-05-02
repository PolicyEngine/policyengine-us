from policyengine_us.model_api import *


class pre_subsidy_rent(Variable):
    value_type = float
    entity = Person
    label = "Pre subsidy rent"
    unit = USD
    definition_period = YEAR
