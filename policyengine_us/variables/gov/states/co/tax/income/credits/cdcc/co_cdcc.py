from policyengine_us.model_api import *

class co_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CO CDCC"
    unit = USD
    definition_period = YEAR
    reference = "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=7aafe5fc-edf6-4051-9e28-5bf4f1318407&nodeid=ABPAACAACAABAACABA&nodepath=%2FROOT%2FABP%2FABPAAC%2FABPAACAAC%2FABPAACAACAAB%2FABPAACAACAABAAC%2FABPAACAACAABAACABA&level=6&haschildren=&populated=false&title=39-22-119.+Expenses+related+to+child+care+-+credits+against+state+tax.&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65HV-06G3-CGX8-050B-00008-00&ecomp=7gf59kk&prid=ac5437c8-99c9-4ca1-9a0d-992cc2141911"  # (c)
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        expenses = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.co.tax.income.credits.cdcc.match
        return expenses * rate