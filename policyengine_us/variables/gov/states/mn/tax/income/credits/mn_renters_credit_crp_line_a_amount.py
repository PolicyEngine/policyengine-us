from policyengine_us.model_api import *


class mn_renters_credit_crp_line_a_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit CRP line A amount"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.MN

