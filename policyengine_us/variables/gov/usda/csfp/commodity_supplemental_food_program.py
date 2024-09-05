from policyengine_us.model_api import *


class commodity_supplemental_food_program(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Commodity Supplemental Food Program"
    defined_for = "commodity_supplemental_food_program_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.csfp
        return p.amount
