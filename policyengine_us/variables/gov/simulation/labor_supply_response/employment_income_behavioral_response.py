from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    earnings_before_lsr,
)


class employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        employment_income = max_(person("employment_income_before_lsr", period), 0)
        total_earnings = earnings_before_lsr(person, period)
        emp_share = np.ones_like(total_earnings)
        mask = total_earnings > 0
        emp_share[mask] = employment_income[mask] / total_earnings[mask]
        return lsr * emp_share
