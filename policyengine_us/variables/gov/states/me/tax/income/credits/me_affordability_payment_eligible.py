from policyengine_us.model_api import *


class me_affordability_payment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine affordability payment eligible"
    defined_for = StateCode.ME
    definition_period = YEAR
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=157"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.affordability_payment
        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        income_eligible = federal_agi < p.income_limit[filing_status]
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        claimed_elsewhere = person("claimed_as_dependent_on_another_return", period)
        any_filer_claimed = tax_unit.any(head_or_spouse & claimed_elsewhere)
        return income_eligible & ~any_filer_claimed
