from policyengine_us.model_api import *


class mt_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Montana refundable credits"
    unit = USD
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=48"
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = [
        "mt_refundable_credits_before_renter_credit",
        "mt_elderly_homeowner_or_renter_credit",
    ]
    # Under the gross income sources computation, the elderly homeowner or renter credit
    # is included in the list of refundable credits
    # This will create a potential circular reference (check reference Line7)
    # mt_refundable_credits_before_renter_credit was created to circumvent this
