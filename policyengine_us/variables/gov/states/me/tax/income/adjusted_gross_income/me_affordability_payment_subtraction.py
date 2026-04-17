from policyengine_us.model_api import *


class me_affordability_payment_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine affordability payment subtraction"
    unit = USD
    documentation = (
        "Amount of the Maine affordability payment received in the tax year and "
        "included in federal AGI."
    )
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=158"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.agi.subtractions.affordability_payment_subtraction
        reported = tax_unit("me_affordability_payment_subtraction_reported", period)
        return p.in_effect * reported
