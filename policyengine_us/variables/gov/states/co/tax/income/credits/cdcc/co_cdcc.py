from policyengine_us.model_api import *


class co_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Child Care Expenses Credit"
    unit = USD
    documentation = (
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=d14880b7-7410-4295-bcf1-2e099e57d8f3&pdistocdocslideraccess=true&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65HV-06G3-CGX8-050B-00008-00&pdcomponentid=234177&pdtocnodeidentifier=ABPAACAACAABAACABA&ecomp=k2vckkk&prid=e2e32763-f8fa-4832-8191-f70124d877f6"
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46"
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        # follow 2022 DR 0347 form and its instructions (in Book cited above):
        p = parameters(period).gov.states.co.tax.income.credits
        fed_agi = tax_unit("adjusted_gross_income", period)  # Line 4
        # calculate regular Colorado CDCC in Part III
        capped_fed_cdcc = tax_unit("capped_cdcc", period)  # Line 8
        match_rate = p.cdcc.match.calc(fed_agi, right=True)
        return capped_fed_cdcc * match_rate  # Line 9
        # calculate low-income Colorado CDCC in Part IV in co_low_income_cdcc
