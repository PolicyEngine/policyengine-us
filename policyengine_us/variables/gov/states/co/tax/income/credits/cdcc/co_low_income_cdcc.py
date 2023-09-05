from policyengine_us.model_api import *


class co_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Low-income Child Care Expenses Credit"
    unit = USD
    documentation = (
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitions"
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46"
    )
    definition_period = YEAR
    defined_for = "co_low_income_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        # follow 2022 DR 0347 form and its instructions (in Book cited above):
        p = parameters(period).gov.states.co.tax.income.credits
        # estimate care expenses for just children
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
        # calculate capped credit amount
        credit = p.cdcc.low_income.rate * capped_kid_expenses  # Line 11
        cap = p.cdcc.low_income.max_amount.calc(eligible_kids)  # Table A
        return min_(credit, cap)  # Line 12
