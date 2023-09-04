from policyengine_us.model_api import *


class co_low_income_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Low-income Child Care Expenses Credit"
    documentation = "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitions"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.cdcc.low_income
        # Filer is eligible if AGI is below $25,000
        agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = agi <= p.income_threshold
        # Filers cannot claim the low income CDCC if they don't have tax liability to
        # claim the non-refundable Colorado CDCC.
        received_fed_cdcc = tax_unit("capped_cdcc", period) > 0
        return ~received_fed_cdcc & agi_eligible
