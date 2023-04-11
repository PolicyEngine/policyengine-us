from policyengine_us.model_api import *


class la_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana income tax before credits"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=101946"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("la_taxable_income", period)
        p = parameters(period).gov.states.la.tax.income.rates
        return p.calc(taxable_income)
