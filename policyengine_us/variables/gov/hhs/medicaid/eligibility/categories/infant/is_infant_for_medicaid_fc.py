from policyengine_us.model_api import *
import numpy as np


class is_infant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.infant

        income = person("medicaid_income_level", period)
        state_code = person.household(
            "state_code_str", period
        )  # e.g. "CA", "NY"
        income_limit = p.income_limit[state_code]
        # allow exactly at the threshold
        return np.isclose(income, income_limit) | (income <= income_limit)
