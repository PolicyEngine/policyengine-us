from openfisca_us.model_api import *


class hud_gross_rent(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD gross rent"
    unit = USD
    documentation = "Gross rent for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/982.503"

    # TODO: Add utility costs.
    formula = sum_of_variables(["housing_cost", "hud_utility_allowance"])
