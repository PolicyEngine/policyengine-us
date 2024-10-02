from policyengine_us.model_api import *


class mt_refundable_credits_before_renter_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana refundable credits before adding the elderly homeowner or renter credit"
    unit = USD
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=48"
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = "gov.states.mt.tax.income.credits.refundable"
    # Under the gross income sources computation, the elderly homeowner or renter credit
    # is included in the list of refundable credits
    # This variable was created to circumvent potential circular reference
