from policyengine_us.model_api import *


class miscellaneous_income(Variable):
    value_type = float
    entity = Person
    label = "Miscellaneous income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.61-14"
