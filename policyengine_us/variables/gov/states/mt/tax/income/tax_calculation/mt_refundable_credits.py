from policyengine_us.model_api import *


class mt_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Montana refundable credits"
    unit = USD
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=48"
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = [
        "mt_refundable_credits_before_renter_credit",
        "mt_elderly_homeowner_or_renter_credit",
        # HB 192 Sec. 2(3) pays the 2021 income tax rebate electronically or by
        # check in 2023. Like Georgia's HB 162 surplus rebate, it is booked to
        # tax year 2021 as a refundable payment (zero in every other year). It
        # stays out of credits/refundable.yaml because that list also feeds the
        # elderly homeowner or renter credit's gross household income (Form 2EC
        # line 7).
        "mt_income_tax_rebate",
    ]
    # Under the gross income sources computation, the elderly homeowner or renter credit
    # is included in the list of refundable credits
    # This will create a potential circular reference (check reference Line7)
    # mt_refundable_credits_before_renter_credit was created to circumvent this
