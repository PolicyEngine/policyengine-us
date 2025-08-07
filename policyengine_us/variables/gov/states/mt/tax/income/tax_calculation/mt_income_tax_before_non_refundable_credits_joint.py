from policyengine_us.model_api import *


class mt_income_tax_before_non_refundable_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = ["mt_capital_gains_tax_joint", "mt_regular_income_tax_joint"]
