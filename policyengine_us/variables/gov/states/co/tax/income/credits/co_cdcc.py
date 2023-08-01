from policyengine_us.model_api import *


class co_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Child Care Expenses Credit"
    unit = USD
    documentation = "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=d14880b7-7410-4295-bcf1-2e099e57d8f3&pdistocdocslideraccess=true&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65HV-06G3-CGX8-050B-00008-00&pdcomponentid=234177&pdtocnodeidentifier=ABPAACAACAABAACABA&ecomp=k2vckkk&prid=e2e32763-f8fa-4832-8191-f70124d877f6"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        rate = p.match.calc(agi)
        return federal_cdcc * rate
