from policyengine_us.model_api import *


class ny_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's NY refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.ny.tax.income.credits.refundable
        rebates = ["ny_inflation_refund_credit"]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
