from policyengine_us.model_api import *
import numpy as np


class is_infant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant financial criteria"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.infant

        income = person("medicaid_income_level", period)
        state_code = person.household("state_code_str", period)  # e.g. "CA", "NY"
        income_limit = p.income_limit[state_code]
        # California's inclusive ceiling must not admit income above the limit
        # through an isclose tolerance. Match the precision of the stored ratio.
        ca_eligible = income <= np.asarray(income_limit, dtype=income.dtype)
        return where(
            state_code == "CA",
            ca_eligible,
            np.isclose(income, income_limit) | (income <= income_limit),
        )
