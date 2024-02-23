from policyengine_us.model_api import *


class co_able_contribution_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado able contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/Book0104_2023.pdf#page=14",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=28da6d1b-814f-4ace-b369-4a0d0233db83&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A689J-29B3-GXF6-81G9-00008-00&pdcontentcomponentid=234176&pdteaserkey=sr2&pditab=allpods&ecomp=bs65kkk&earg=sr2&prid=a5cd01c5-3332-4547-a3ff-d2bd6bcc868f",
        # C.R.S. 39-22-104(4)(i)(II)(B)
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        contribution_amount = tax_unit("able_contributions", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.able_contribution
        cap_amount = p.cap[tax_unit("filing_status", period)]
        return min_(contribution_amount, cap_amount)
