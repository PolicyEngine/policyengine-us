from policyengine_us.model_api import *


class self_employment_income_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "self-employment income behavioral response"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        lsr = person("labor_supply_behavioral_response", period)
        employment_response = person("employment_income_behavioral_response", period)
        total_self_employment_response = lsr - employment_response
        non_sstb_self_employment_income = abs(
            person("self_employment_income_before_lsr", period)
        )
        sstb_self_employment_income = abs(
            person("sstb_self_employment_income_before_lsr", period)
        )
        total_self_employment_income = (
            non_sstb_self_employment_income + sstb_self_employment_income
        )
        non_sstb_share = np.divide(
            non_sstb_self_employment_income,
            total_self_employment_income,
            out=np.ones_like(total_self_employment_income),
            where=total_self_employment_income > 0,
        )
        return total_self_employment_response * non_sstb_share
