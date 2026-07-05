from policyengine_us.model_api import *


class hud_earned_income(Variable):
    value_type = float
    entity = Person
    label = "HUD earned income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.609"
    adds = "gov.hud.annual_income.sources.earned"
