from policyengine_us.model_api import *


class ma_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's MA refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.ma.tax.income.credits.refundable
        rebates = [
            "ma_covid_19_essential_employee_premium_pay_program",
            "ma_taxpayer_refund_rebate",
        ]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
