from policyengine_us.model_api import *


class ca_riv_general_relief_net_earned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Riverside County GA net earned income after deductions"
    definition_period = MONTH

    def formula(person, period, parameters):
        earned = person("ca_riv_general_relief_earned_income", period)
        deductions = person(
            "ca_riv_general_relief_earned_income_deductions", period
        )

        return max_(earned - deductions, 0)
