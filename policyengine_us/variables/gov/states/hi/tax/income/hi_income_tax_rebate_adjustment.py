from policyengine_us.model_api import *


class hi_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "HI income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's HI refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.hi.tax.income.credits.refundable
        rebates = ["hi_act_115_rebate"]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
