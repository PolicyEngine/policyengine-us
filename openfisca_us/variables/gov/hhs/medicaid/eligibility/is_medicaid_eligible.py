from openfisca_us.model_api import *


class is_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#a_10"

    def formula(person, period, parameters):
        category = person("medicaid_category", period)
        return category != category.possible_values.NONE
