from policyengine_us.model_api import *


class co_collegeinvest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado collegeinvest deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=49fe2864-b8f7-4db8-8819-3b6d1cabfe53&action=pawlinkdoc&pdcomponentid=&pddocfullpath=%2fshared%2fdocument%2fstatutes-legislation%2furn%3acontentItem%3a683G-JJ73-CGX8-04HR-00008-00&pdtocnodeidentifier=ABPAACAACAABAACAAF&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&ecomp=k2vckkk&prid=b4d7981f-7c6f-4802-8aa4-8d4c7a85c292"
        # C.R.S. 39-22-104(4)(i)(II)(B)
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        collegeinvest_amount = add(
            tax_unit, period, ["co_collegeinvest_amount"]
        )
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.collegeinvest_contribution
        cap = p.max_amount[tax_unit("filing_status", period)]
        return min_(collegeinvest_amount, cap)
