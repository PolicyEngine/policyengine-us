from policyengine_us.model_api import *


class commodity_supplemental_food_program(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Commodity Supplemental Food Program"
    defined_for = "commodity_supplemental_food_program_eligible"
    adds = ["gov.usda.csfp.amount"]
