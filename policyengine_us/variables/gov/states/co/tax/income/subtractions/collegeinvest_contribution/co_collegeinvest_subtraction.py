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
        # C.R.S. 39-22-104(4)(i)(II)(B)-(C), PDF pages 392-393.
        "https://content.leg.colorado.gov/sites/default/files/images/olls/crs2024-title-39.pdf#page=392",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        investment_amount = tax_unit("investment_in_529_plan", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.collegeinvest_contribution
        cap = p.max_amount[tax_unit("filing_status", period)]
        return min_(investment_amount, cap)
