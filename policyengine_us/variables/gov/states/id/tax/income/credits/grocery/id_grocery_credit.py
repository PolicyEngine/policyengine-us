from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = "id_grocery_credit_eligible"

    def formula(tax_unit, period, parameters):
        adds = ["id_grocery_credit_base", "id_grocery_credit_aged"]
