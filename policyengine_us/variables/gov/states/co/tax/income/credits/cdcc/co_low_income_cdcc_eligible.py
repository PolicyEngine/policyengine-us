from policyengine_us.model_api import *


class co_low_income_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Low-income Child Care Expenses Credit"
    documentation = (
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitions"
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46"
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        no_fed_cdcc = tax_unit("capped_cdcc", period) <= 0
        p = parameters(period).gov.states.co.tax.income.credits
        fed_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = fed_agi <= p.cdcc.low_income.federal_agi_threshold
        return no_fed_cdcc & agi_eligible
