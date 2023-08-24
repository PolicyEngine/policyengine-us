from policyengine_us.model_api import *


class co_itemized_or_standard_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado itemized or standard deductions"
    unit = USD
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
        ).gov.states.co.tax.income.additions.co_itemized_or_standard_deductions
        agi_eligiblity = (
            tax_unit("adjusted_gross_income", period) > p.agi_threshold
        )
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        limit = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.WIDOW,
            ],
            [
                p.limits.single,
                p.limits.joint,
                p.limits.head_of_household,
                p.limits.separate,
                p.limits.widow,
            ],
        )
        federal_itemized_deduction = (
            tax_unit("itemized_taxable_income_deductions", period)
            * p.is_itemized_deductions
        )
        federal_standard_deduction = (
            tax_unit("standard_deduction", period) * p.is_standard_deductions
        )
        return (
            max_(
                0,
                federal_itemized_deduction
                + federal_standard_deduction
                - limit,
            )
            * agi_eligiblity
        )
