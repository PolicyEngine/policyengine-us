from policyengine_us.model_api import *


class az_wood_stove_conversion_expense(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona wood stove or fireplace conversion expense"
    unit = USD
    documentation = (
        "Cost of converting a wood burning fireplace to a qualified gas fired "
        "fireplace or a qualified wood stove meeting EPA standards."
    )
    definition_period = YEAR
