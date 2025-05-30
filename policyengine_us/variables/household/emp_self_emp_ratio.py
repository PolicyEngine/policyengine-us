from policyengine_us.model_api import *


class emp_self_emp_ratio(Variable):
    value_type = float
    entity = Person
    label = "Share of earnings from wages and salaries"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1402"

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        earnings = employment_income + self_employment_income
        res = np.ones_like(earnings)
        mask = earnings > 0
        res[mask] = employment_income[mask] / earnings[mask]
        return res
