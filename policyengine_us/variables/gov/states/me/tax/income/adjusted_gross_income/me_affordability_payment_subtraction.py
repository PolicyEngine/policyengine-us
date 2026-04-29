from policyengine_us.model_api import *


class me_affordability_payment_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine affordability payment subtraction"
    unit = USD
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=158"
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = (
        "Sec. T-1, sub-§4 allows Maine taxpayers to subtract from FAGI the "
        "portion of the affordability payment that was included in FAGI, "
        "for tax years 2026 and 2027 only. We rely on "
        "me_affordability_payment_subtraction_reported to capture the "
        "amount actually included in FAGI, since the IRS treatment of "
        "the payment is not yet final."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.agi.subtractions.affordability_payment_subtraction
        if p.in_effect:
            return tax_unit("me_affordability_payment_subtraction_reported", period)
        return 0
