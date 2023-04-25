from policyengine_us.model_api import *


class nd_ltcg_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "ND long-term capital gains subtraction from federal taxable income"
    )
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
        ltcg = add(tax_unit, period, ["long_term_capital_gains"])
        stcg = add(tax_unit, period, ["short_term_capital_gains"])
        net_ltcg = min_(ltcg, ltcg + stcg)
        p = parameters(period).gov.states.nd.tax.income
        return net_ltcg * p.taxable_income.subtractions.ltcg_fraction
