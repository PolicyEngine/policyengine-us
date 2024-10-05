from policyengine_us.model_api import *


class taxable_sep_distributions(Variable):
    value_type = float
    entity = Person
    label = "taxable SEP distributions"
    unit = USD
    definition_period = YEAR
