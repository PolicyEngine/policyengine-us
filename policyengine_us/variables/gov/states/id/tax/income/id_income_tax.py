from policyengine_us.model_api import *


class id_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    adds = ["id_income_tax_before_refundable_credits", "id_pbf"]
    subtracts = ["id_refundable_credits"]
