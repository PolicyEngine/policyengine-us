from policyengine_us.model_api import *


class me_relief_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine Relief Rebate eligible"
    defined_for = StateCode.ME
    definition_period = YEAR
    reference = "https://www.maine.gov/governor/mills/relief-checks"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.relief_rebate
        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        income_threshold = p.income_limit[filing_status]
        return federal_agi < income_threshold
