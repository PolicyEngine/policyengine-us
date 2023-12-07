from policyengine_us.model_api import *


class mt_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana refundable credits"
    unit = USD
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=48"
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = [
        "mt_refundable_credits_before_renter_credit",
        "mt_elderly_homeowner_or_renter_credit",
    ]
    # In gross income sources, we include the elderly homeowner or renter credit in refundable credits
    # This will create a circular reference (check reference Line7)
    # So we created another variable mt_refundable_credits_before_renter_credit.py
