from openfisca_us.model_api import *


class is_older_child_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid older child non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.older_child
        age = person("age", period)
        return ma.age_range.calc(age)
