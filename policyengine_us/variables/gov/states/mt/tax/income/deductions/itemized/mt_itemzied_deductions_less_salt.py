from policyengine_us.model_api import *


class mt_itemized_deductions_less_salt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana itemized deductions excluding SALT"
    unit = USD
    definition_period = YEAR
    adds = ["mt_itemzied_deductions"]
    subtracts = ["mt_salt_deductions"]
    