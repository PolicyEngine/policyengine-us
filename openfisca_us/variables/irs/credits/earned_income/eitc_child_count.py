from openfisca_us.model_api import *


class eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "EITC-qualifying children"
    unit = USD
    documentation = "Number of children qualifying as children for the EITC."
    definition_period = YEAR

    formula = sum_of_variables(["is_eitc_qualifying_child"])
