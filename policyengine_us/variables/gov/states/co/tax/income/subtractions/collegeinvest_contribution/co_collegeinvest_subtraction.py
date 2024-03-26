from policyengine_us.model_api import *


class co_collegeinvest_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado collegeinvest subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(4)(i)(II)(B)
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        investment_amount = tax_unit("investment_in_529_plan", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.collegeinvest_contribution
        cap = p.max_amount[tax_unit("filing_status", period)]
        return min_(investment_amount, cap)
