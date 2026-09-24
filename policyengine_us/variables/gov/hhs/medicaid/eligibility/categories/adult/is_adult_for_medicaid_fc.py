from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_adult_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid adult financial criteria"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.119"

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.adult
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return medicaid_income_eligible(person, period, parameters, income_limit)
