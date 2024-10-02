from policyengine_us.model_api import *


class va_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = "va_must_file"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("va_taxable_income", period)
        p = parameters(period).gov.states.va.tax.income.rates
        return p.calc(taxable_income)
