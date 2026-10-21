from policyengine_us.model_api import *


class co_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "CO income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's CO refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.co.tax.income.credits.refundable
        rebates = ["co_sales_tax_refund", "co_tabor_cash_back"]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
