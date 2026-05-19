from policyengine_us.model_api import *


class me_affordability_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine affordability payment"
    defined_for = "me_affordability_payment_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=157"
    documentation = (
        "Sec. T-1, sub-§3 defines the affordability payment as a direct "
        "payment from a Special Revenue Fund rather than a refundable tax "
        "credit. PolicyEngine folds the payment into Maine's refundable "
        "credit aggregation to surface it in tax-unit-level outputs. "
        "Sec. T-1, sub-§1(C)(3) excludes individuals claimed as a "
        "dependent on another taxpayer's return, evaluated per recipient."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.affordability_payment
        person = tax_unit.members
        is_recipient = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        dependent_elsewhere = person("claimed_as_dependent_on_another_return", period)
        eligible_recipients = tax_unit.sum(is_recipient & ~dependent_elsewhere)
        return eligible_recipients * p.amount
