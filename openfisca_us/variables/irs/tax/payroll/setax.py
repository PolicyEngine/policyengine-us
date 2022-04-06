from openfisca_us.model_api import *


class setax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment payroll tax"
    definition_period = YEAR
    unit = USD

    formula = sum_of_variables(
        ["self_employment_social_security_tax", "self_employment_medicare_tax"]
    )
