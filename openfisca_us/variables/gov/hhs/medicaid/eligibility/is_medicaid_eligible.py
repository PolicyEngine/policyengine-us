from openfisca_us.model_api import *


class is_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid financial criteria"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        person_type = person("medicaid_person_type", period)
        person_types = person_type
        return select(
            [
                person_type == person_types.AGED_BLIND_DISABLED,
                True,
            ],
            [
                person("meets_medicaid_disabled_income_test", period),
                person("meets_medicaid_income_threshold", period),
            ],
        )
