from openfisca_us.model_api import *


class housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "is_eligible_for_housing_assistance"

    formula = sum_of_variables(["hud_hap"])
