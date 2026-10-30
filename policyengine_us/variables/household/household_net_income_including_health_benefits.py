from policyengine_us.model_api import *


class household_net_income_including_health_benefits(Variable):
    value_type = float
    entity = Household
    label = "Net income including health benefits"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        household_net_income = household("household_net_income", period)
        if parameters(period).gov.simulation.include_health_benefits_in_net_income:
            return household_net_income
        healthcare_benefit_value = household("healthcare_benefit_value", period)
        return household_net_income + healthcare_benefit_value
