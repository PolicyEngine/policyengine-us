from policyengine_us.model_api import *


class ar_inflation_relief_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas inflation relief income-tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    adds = ["ar_inflation_relief_credit_person"]
