from policyengine_us.model_api import *


class co_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        # C.R.S. 39-22-129. Child tax credit - legislative declaration - definitions.
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=4f86a852-765a-489a-b554-66f6e7d5b065&nodeid=ABPAACAACAABAACABN&nodepath=%2fROOT%2fABP%2fABPAAC%2fABPAACAAC%2fABPAACAACAAB%2fABPAACAACAABAAC%2fABPAACAACAABAACABN&level=6&haschildren=&populated=false&title=39-22-129.+Child+tax+credit+-+legislative+declaration+-+definitions.&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2fshared%2fdocument%2fstatutes-legislation%2furn%3acontentItem%3a633G-B1C3-GXJ9-30GW-00008-00&ecomp=7gf59kk&prid=2fe6fa8e-8df8-4d74-a340-c4fa9bc603d5",
        # 2022 Colorado Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1",
        # Colorado Individual Income Tax Filing Guide - Instructions for Select Credits from the DR 0104CR - Line 1 Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16",
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        person = tax_unit.members
        # The co ctc amount is based on agi, federal ctc amount and number of eligible children.
        agi = tax_unit("adjusted_gross_income", period)
        federal_ctc = tax_unit("ctc", period)

        eligible_child = person("age", period) < p.age_threshold
        eligible_children = tax_unit.sum(eligible_child)

        rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
            ],
        )
        return rate * federal_ctc * eligible_children
