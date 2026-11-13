from policyengine_us.model_api import *


class nm_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "NM income tax rebate adjustment"
    documentation = (
        "Rebates included in this year's NM refundable-credit total. "
        "Only registered rebates in the dated credit list are restored; "
        "ordinary credits and other credit calculations remain unchanged."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.states.nm.tax.income.credits.refundable
        rebates = [
            "nm_2021_income_rebate",
            "nm_additional_2021_income_rebate",
            "nm_supplemental_2021_income_rebate",
        ]
        included = [rebate for rebate in rebates if rebate in credits]
        return add(tax_unit, period, included) if included else 0
