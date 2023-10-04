from policyengine_us.model_api import *


class id_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    adds = ["id_additions", "adjusted_gross_income"]
    subtracts = ["id_subtractions"]
