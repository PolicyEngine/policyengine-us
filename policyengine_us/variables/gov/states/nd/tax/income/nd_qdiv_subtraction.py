from policyengine_us.model_api import *


class nd_qdiv_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ND qualified dividends subtraction from federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2021-individual-income-tax-booklet.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        qdiv = add(tax_unit, period, ["qualified_dividend_income"])
        p = parameters(period).gov.states.nd.tax.income
        return qdiv * p.taxable_income.subtractions.qdiv_fraction
