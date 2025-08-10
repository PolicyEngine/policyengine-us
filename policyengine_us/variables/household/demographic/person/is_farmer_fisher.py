from policyengine_us.model_api import *


class is_farmer_fisher(Variable):
    value_type = bool
    entity = Person
    label = "is employed in a farming, fishing, cultivating, or agriculture related occupation"
    reference = "https://www.law.cornell.edu/uscode/text/29/213"
    definition_period = YEAR
