from policyengine_us.model_api import *


class me_affordability_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine affordability payment"
    defined_for = "me_affordability_payment_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=2&snum=132#page=158"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.affordability_payment
        head_spouse_count = tax_unit("head_spouse_count", period)
        return head_spouse_count * p.amount
