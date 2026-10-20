from policyengine_us.model_api import *


class il_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's IL refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.il.tax.income.credits.refundable
        rebates = ["il_income_tax_rebate", "il_property_tax_rebate"]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
