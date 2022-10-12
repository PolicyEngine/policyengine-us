from policyengine_us.model_api import *


class self_employment_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment tax"
    definition_period = YEAR
    unit = USD

    formula = sum_of_variables(
        ["self_employment_social_security_tax", "self_employment_medicare_tax"]
    )
