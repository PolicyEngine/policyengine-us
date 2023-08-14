from policyengine_us.model_api import *


class co_salt_refund_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado state and local tax refund income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=11",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=39ef3d29-d741-4246-8de2-03c3bbddac3b&action=pawlinkdoc&pdcomponentid=&pddocfullpath=%2fshared%2fdocument%2fstatutes-legislation%2furn%3acontentItem%3a683G-JJ73-CGX8-04HR-00008-00&pdtocnodeidentifier=ABPAACAACAABAACAAF&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&ecomp=k2vckkk&prid=49fe2864-b8f7-4db8-8819-3b6d1cabfe53"
        # C.R.S. 39-22-104(4)(e)
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        salt_refund_income = person("salt_refund_income", period)
        s1_form1040 = tax_unit("tax_unit_s1_form1040", period)
        return s1_form1040 * salt_refund_income
