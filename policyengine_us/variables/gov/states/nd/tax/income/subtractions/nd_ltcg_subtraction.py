from policyengine_us.model_api import *


class nd_ltcg_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota long-term capital gains subtraction from federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1"  # line 7
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1"  # line 7
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        ltcg = add(tax_unit, period, ["long_term_capital_gains"])
        stcg = add(tax_unit, period, ["short_term_capital_gains"])
        net_ltcg = min_(ltcg, ltcg + stcg)
        p = parameters(period).gov.states.nd.tax.income
        return net_ltcg * p.taxable_income.subtractions.ltcg_fraction
