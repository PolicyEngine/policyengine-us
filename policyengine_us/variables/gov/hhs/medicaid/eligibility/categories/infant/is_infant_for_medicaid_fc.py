from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_infant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant financial criteria"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.118",
        "https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.infant

        state_code = person.household("state_code_str", period)  # e.g. "CA", "NY"
        income_limit = p.income_limit[state_code]
        return medicaid_income_eligible(person, period, parameters, income_limit)
