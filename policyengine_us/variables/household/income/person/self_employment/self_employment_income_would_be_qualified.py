from policyengine_us.model_api import *


class self_employment_income_would_be_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Self-employment income would be qualified"
    documentation = "Whether self-employment income would be considered qualified business income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c_3_A"
    default_value = True
