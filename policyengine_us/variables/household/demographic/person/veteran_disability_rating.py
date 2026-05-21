from policyengine_us.model_api import *


class veteran_disability_rating(Variable):
    value_type = int
    entity = Person
    label = "The overall veteran disability rating for the individual"
    definition_period = YEAR
    default_value = 0
    reference = "https://www.law.cornell.edu/uscode/text/38/1155"

