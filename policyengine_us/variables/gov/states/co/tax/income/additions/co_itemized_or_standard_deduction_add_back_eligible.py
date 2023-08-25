from policyengine_us.model_api import *


class co_itemized_or_standard_deduction_add_back_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado itemized or standard deduction add back"
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3)(p) - (p.5)
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=0ac0632f-7202-4eec-b761-6e36fad6542d&action=pawlinkdoc&pdcomponentid=&pddocfullpath=%2fshared%2fdocument%2fstatutes-legislation%2furn%3acontentItem%3a683G-JJ73-CGX8-04HR-00008-00&pdtocnodeidentifier=ABPAACAACAABAACAAF&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&ecomp=k2vckkk&prid=713552e7-276b-4575-a579-ea86a2ff3c84",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions - Line 4
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income - Federal itemized or standard deductions
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.additions.itemized_or_standard_deduction_add_back
        return tax_unit("adjusted_gross_income", period) > p.agi_threshold
