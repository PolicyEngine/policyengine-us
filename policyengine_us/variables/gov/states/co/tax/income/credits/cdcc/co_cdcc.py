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
    reference = (
        # C.R.S. 39-22-119(1.7) (2026+ regime added by HB24-1134, SECTION 1)
        "https://leg.colorado.gov/sites/default/files/2024a_1134_signed.pdf#page=3",
        # Income Tax Topics: Child and Dependent Care Expenses Credit (Revised January 2026)
        "https://tax.colorado.gov/sites/tax/files/documents/ITT_Child_and_Dependent_Care_Expenses_Credit_Jan_2026.pdf",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits
        fed_agi = tax_unit("adjusted_gross_income", period)  # Line 4
        if p.cdcc.uses_federal_credit_before_liability_limitation:
            # C.R.S. 39-22-119(1.7)(b): for income tax years beginning on and
            # after January 1, 2026, the credit is 70% of the federal section
            # 21 credit calculated without regard to the section 26 tax-
            # liability limitation, for filers with federal AGI at or below the
            # limit. cdcc_potential is the federal credit before the liability
            # limitation; capped_cdcc and cdcc apply that limitation.
            fed_cdcc_before_limit = tax_unit("cdcc_potential", period)
            agi_eligible = fed_agi <= p.cdcc.max_agi
            return agi_eligible * p.cdcc.rate * fed_cdcc_before_limit
        # Before 2026, follow the 2022 DR 0347 form and its instructions:
        # the credit is an income-graduated match of the federal credit the
        # taxpayer actually claimed and was allowed (after the liability cap).
        capped_fed_cdcc = tax_unit("capped_cdcc", period)  # Line 8
        match_rate = p.cdcc.match.calc(fed_agi, right=True)
        return capped_fed_cdcc * match_rate  # Line 9
        # calculate low-income Colorado CDCC in Part IV in co_low_income_cdcc
        # (repealed for tax years beginning on or after January 1, 2026)
