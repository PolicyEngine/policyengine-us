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
        head_dependent = tax_unit("head_is_dependent_elsewhere", period)
        spouse_dependent = tax_unit("spouse_is_dependent_elsewhere", period)
        return income_eligible & ~head_dependent & ~spouse_dependent
