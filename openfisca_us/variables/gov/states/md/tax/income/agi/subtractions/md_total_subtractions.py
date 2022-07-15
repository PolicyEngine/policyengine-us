from openfisca_us.model_api import *


class md_total_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total subtractions from AGI"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["md_dependent_care_subtraction"])
