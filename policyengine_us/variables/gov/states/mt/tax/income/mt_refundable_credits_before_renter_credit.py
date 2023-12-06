from policyengine_us.model_api import *


class mt_refundable_credits_before_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        mt_refundable_credits = tax_unit("mt_refundable_credits", period)
        mt_elderly_homeowner_or_renter_credit = tax_unit(
            "mt_elderly_homeowner_or_renter_credit", period
        )
        return max_(
            mt_refundable_credits - mt_elderly_homeowner_or_renter_credit, 0
        )
