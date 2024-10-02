from policyengine_us.model_api import *


class nd_qdiv_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota qualified dividends subtraction from federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1"  # line 13
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=15"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1"  # line 13
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=15"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        qdiv = add(tax_unit, period, ["qualified_dividend_income"])
        p = parameters(period).gov.states.nd.tax.income
        return qdiv * p.taxable_income.subtractions.qdiv_fraction
