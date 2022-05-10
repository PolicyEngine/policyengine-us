from openfisca_us.model_api import *


class meets_medicaid_disabled_financial_criteria(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid disabled income and asset tests"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        meets_income_test = person(
            "meets_medicaid_disabled_income_test", period
        )
        meets_asset_test = person("meets_medicaid_disabled_asset_test", period)
        return meets_income_test & meets_asset_test
