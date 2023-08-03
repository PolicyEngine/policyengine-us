from policyengine_us.model_api import *


class hud_annual_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD annual income"
    unit = USD
    documentation = "Annual income for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.609"

    adds = ["market_income"]
