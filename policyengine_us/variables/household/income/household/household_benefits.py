from policyengine_us.model_api import *


class household_benefits(Variable):
    value_type = float
    entity = Household
    label = "benefits"
    unit = USD
    definition_period = YEAR

    def formula(household, period, parameters):
        BENEFITS = list(parameters(period).gov.household.household_benefits)
        if parameters(period).gov.hud.abolition:
            BENEFITS = [
                benefit
                for benefit in BENEFITS
                if benefit != "spm_unit_capped_housing_subsidy"
            ]
        return add(household, period, BENEFITS)
