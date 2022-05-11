from openfisca_us.model_api import *


class meets_medicaid_disabled_income_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid disabled income test"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        limit = parameters(
            period
        ).hhs.medicaid.aged_or_disabled.income_limit
        state = person.household("state_code_str", period)
        income_share_of_fpg = person.spm_unit("medicaid_income_level", period)
        return income_share_of_fpg <= limit[state]
