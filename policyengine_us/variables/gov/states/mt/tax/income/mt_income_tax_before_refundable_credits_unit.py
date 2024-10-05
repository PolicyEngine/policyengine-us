from policyengine_us.model_api import *


class mt_income_tax_before_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        income_tax_before_credits_indiv = add(
            tax_unit, period, ["mt_income_tax_before_refundable_credits_indiv"]
        )
        income_tax_before_credits_joint = tax_unit(
            "mt_income_tax_before_refundable_credits_joint", period
        )
        return min_(
            income_tax_before_credits_indiv, income_tax_before_credits_joint
        )
