from policyengine_us.model_api import *


class mt_income_tax_before_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Elected income tax before refundable credits, then reduced by the
        # 2021 income tax rebate (a one-time payment based on the return's
        # liability), so the rebate flows through to state_income_tax without
        # being clipped per column or distorting the election (taxsim #1189).
        before_rebate = tax_unit("mt_income_tax_before_2021_rebate", period)
        rebate = tax_unit("mt_income_tax_rebate", period)
        return max_(before_rebate - rebate, 0)
