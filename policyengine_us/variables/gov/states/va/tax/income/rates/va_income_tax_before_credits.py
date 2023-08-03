from policyengine_us.model_api import *


class va_income_tax_before_credits(Variable):
    value_type = int
    entity = TaxUnit
    label = "Virginia income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("va_taxable_income", period)
        p = parameters(period).gov.states.va.tax.income.rates
        va_income_tax_before_credits = p.calc(taxable_income)
        return int(np.floor(va_income_tax_before_credits + 0.5))
