from policyengine_us.model_api import *


class employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = employment_income + self_employment_income
        emp_share = np.ones_like(earnings)
        mask = earnings > 0
        emp_share[mask] = employment_income[mask] / earnings[mask]
        return lsr * emp_share