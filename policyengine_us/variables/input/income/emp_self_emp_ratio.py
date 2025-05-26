from policyengine_us.model_api import *


class emp_self_emp_ratio(Variable):
    value_type = float
    entity = Person
    label = "employment-to-self-employment income ratio"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        earnings = employment_income + self_employment_income
        res = np.ones_like(earnings)
        mask = earnings > 0
        res[mask] = employment_income[mask] / earnings[mask]
        return res
