from openfisca_us.model_api import *


class medicaid(Variable):
    value_type = float
    entity = Person
    label = "Medicaid"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
    defined_for = "is_medicaid_eligible"

    formula = sum_of_variables(["medicaid_benefit_value"])
