from openfisca_us.model_api import *


class meets_medicaid_disabled_non_financial_criteria(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid disabled income and asset tests"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        is_blind = person("is_blind", period)
        is_disabled = person("is_disabled", period)
        age = person("age", period)
        ma = parameters(period).hhs.medicaid
        is_aged = age > ma.aged_or_disabled.aged_threshold
        return is_blind & is_disabled & is_aged
