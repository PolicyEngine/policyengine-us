from policyengine_us.model_api import *


class me_affordability_payment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine affordability payment eligible"
    defined_for = StateCode.ME
    definition_period = YEAR
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=157"
    documentation = (
        "Whether the tax unit's federal AGI falls below the affordability "
        "payment income limit for its filing status. Per-recipient "
        "dependent-elsewhere disqualifications are applied in "
        "me_affordability_payment. Sec. T-1 also conditions eligibility on "
        "full-year Maine residency and filing the 2025 return by Oct 15, "
        "2026; PolicyEngine assumes filers are full-year residents and does "
        "not model return-filing dates."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.affordability_payment
        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        return federal_agi < p.income_limit[filing_status]
