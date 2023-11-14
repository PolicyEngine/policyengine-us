from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.alternative_tax
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("taxable_income", period)
        cap = p.income_threshold[filing_status]
        income_eligible = taxable_income > cap

        if p.enables_capital_gains_tax:
            return income_eligible
        else:
            return False
