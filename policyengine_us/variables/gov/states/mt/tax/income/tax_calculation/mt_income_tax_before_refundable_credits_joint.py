from policyengine_us.model_api import *


class mt_income_tax_before_refundable_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        income_before_credits = tax_unit(
            "mt_income_tax_before_non_refundable_credits_joint", period
        )
        non_refundable_credits = add(
            tax_unit, period, ["mt_non_refundable_credits"]
        )
        return max_(income_before_credits - non_refundable_credits, 0)
