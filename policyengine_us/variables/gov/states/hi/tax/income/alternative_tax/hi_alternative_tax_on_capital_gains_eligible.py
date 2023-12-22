from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Hawaii alternative tax on capital gains"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.alternative_tax
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("hi_taxable_income", period)
        income_threshold = p.income_threshold[filing_status]
        income_eligible = taxable_income > income_threshold
        return p.availability & income_eligible
