from policyengine_us.model_api import *


class mt_income_tax_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit("mt_income_tax_before_refundable_credits_joint", period)
        refundable_credits = add(
            tax_unit, period, ["mt_refundable_credits"]
        )
        return income_tax_before_credits - refundable_credits
