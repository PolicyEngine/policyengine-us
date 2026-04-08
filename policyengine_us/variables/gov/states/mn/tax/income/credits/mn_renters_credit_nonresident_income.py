from policyengine_us.model_api import *


class mn_renters_credit_nonresident_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income received while a nonresident of Minnesota for the renter's credit"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.MN

