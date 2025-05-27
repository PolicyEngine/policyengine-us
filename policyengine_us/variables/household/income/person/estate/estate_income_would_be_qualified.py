from policyengine_us.model_api import *


class estate_income_would_be_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Estate income would be qualified"
    documentation = "Whether income from estates would be considered qualified business income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c_3_A"
    default_value = True
