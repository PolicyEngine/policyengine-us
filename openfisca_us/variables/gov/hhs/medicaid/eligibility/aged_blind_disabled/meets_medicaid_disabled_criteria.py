from openfisca_us.model_api import *


class meets_medicaid_disabled_criteria(Variable):
    value_type = bool
    entity = Person
    label = "Qualifies for Medicaid as aged/blind/disabled"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        meets_financial_criteria = person(
            "meets_medicaid_disabled_financial_criteria", period
        )
        meets_non_financial_criteria = person(
            "meets_medicaid_disabled_non_financial_criteria", period
        )
        return meets_financial_criteria & meets_non_financial_criteria
