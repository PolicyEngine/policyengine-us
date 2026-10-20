from policyengine_us.model_api import *


class ct_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "CT income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's CT refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.ct.tax.income.credits.refundable
        rebates = ["ct_child_tax_rebate"]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
