from policyengine_us.model_api import *


class is_infant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.infant
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)

        # Perform a vectorized lookup for income limits for each person by iterating over the state codes.
        income_limit = np.array([ma.income_limit[s] for s in state])
        return income < income_limit
