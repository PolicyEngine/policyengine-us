from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_parent_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid parent financial criteria"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.110"

    def formula(person, period, parameters):
        income_limit = person("medicaid_parent_income_limit", period)
        return medicaid_income_eligible(person, period, parameters, income_limit)
