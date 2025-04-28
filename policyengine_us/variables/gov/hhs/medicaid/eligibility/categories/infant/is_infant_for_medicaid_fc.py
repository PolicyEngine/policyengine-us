from policyengine_us.model_api import *


class is_infant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.infant

        income = person("medicaid_income_level", period)
        state_code = person.household("state_code_str", period)  # e.g. "CA", "NY"

        # **directly index** the income_limit map by the state-code vector
        income_limit = ma.income_limit[state_code]

        # allow exactly at the threshold
        return income < income_limit
