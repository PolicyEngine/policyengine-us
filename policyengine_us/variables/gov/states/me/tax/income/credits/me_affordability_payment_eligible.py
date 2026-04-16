from policyengine_us.model_api import *


class me_affordability_payment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine affordability payment eligible"
    defined_for = StateCode.ME
    definition_period = YEAR
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=2&snum=132#page=158"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.affordability_payment

        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        income_eligible = federal_agi < p.income_limit[filing_status]

        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        dependent = person("is_tax_unit_dependent", period)
        claimed_as_dependent = tax_unit.any(head_or_spouse & dependent)

        return income_eligible & ~claimed_as_dependent
