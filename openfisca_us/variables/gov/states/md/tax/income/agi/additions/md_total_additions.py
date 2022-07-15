from openfisca_us.model_api import *


class md_total_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total additions to AGI"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["md_qualified_tuition_expenses"])
