from policyengine_us.model_api import *


class is_computer_scientist(Variable):
    value_type = bool
    entity = Person
    label = "is employed in a computer science related occupation"
    reference = "https://www.law.cornell.edu/uscode/text/29/213"
    definition_period = YEAR
