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
        itaxbc = tax_unit("income_tax_before_credits", period)  # Line 6
        # calculate regular Colorado CDCC in Part III
        capped_fed_cdcc = tax_unit("capped_cdcc", period)  # Line 8
        match_rate = p.cdcc.match.calc(fed_agi, right=True)
        regular_cdcc = capped_fed_cdcc * match_rate  # Line 9
        # calculate low-income Colorado CDCC in Part IV
        # ... conditions required to complete Part IV
        no_fed_cdcc = capped_fed_cdcc <= 0
        agi_eligible = fed_agi <= p.cdcc.low_income.federal_agi_threshold
        # ... estimate care expenses for just children
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        age = tax_unit.members("age", period)
        eligible_kid = age < p.cdcc.low_income.child_age_threshold
        eligible_kids = tax_unit.sum(eligible_kid)
        total_eligibles = tax_unit("count_cdcc_eligible", period)
        eligible_kid_ratio = np.zeros_like(total_eligibles)
        mask = total_eligibles > 0
        eligible_kid_ratio[mask] = eligible_kids[mask] / total_eligibles[mask]
        kid_expenses = care_expenses * eligible_kid_ratio
        capped_kid_expenses = min_(  # Line 3
            kid_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # ... calculate capped credit amount
        lowinc_credit = p.cdcc.low_income.rate * capped_kid_expenses  # Line 11
        lowinc_cap = p.cdcc.low_income.max_amount.calc(eligible_kids)  # TableA
        lowinc_cdcc = where(  # Line 12
            no_fed_cdcc & agi_eligible, min_(lowinc_credit, lowinc_cap), 0
        )
        return regular_cdcc + lowinc_cdcc
