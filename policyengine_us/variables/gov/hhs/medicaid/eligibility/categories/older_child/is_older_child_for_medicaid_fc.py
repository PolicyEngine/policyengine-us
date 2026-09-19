from policyengine_us.model_api import *


class is_older_child_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid older child financial criteria"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=2"

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.older_child
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        # California's ceiling is inclusive. Compare at the stored income
        # ratio's precision so exactly 266% is not rejected by float32 rounding.
        ca_eligible = income <= np.asarray(income_limit, dtype=income.dtype)
        return where(state == "CA", ca_eligible, income < income_limit)
