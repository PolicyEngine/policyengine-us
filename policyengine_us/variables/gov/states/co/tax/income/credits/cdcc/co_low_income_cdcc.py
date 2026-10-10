from policyengine_us.model_api import *


class co_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Low-income Child Care Expenses Credit"
    unit = USD
    reference = (
        "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-1/section-39-22-119-5/",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46",
        # Income Tax Topics: Low-income Child Care Expenses Credit (January
        # 2026): the taxpayer "would have been allowed to claim a federal child
        # care credit if they had a federal income tax liability".
        "https://tax.colorado.gov/sites/tax/files/documents/ITT_Low-Income_Child_Care_Expenses_Credit_Jan_2026.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    definition_period = YEAR
    defined_for = "co_low_income_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        # follow 2022 DR 0347 form and its instructions (in Book cited above):
        p = parameters(period).gov.states.co.tax.income.credits
        # estimate care expenses for just children
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        age = tax_unit.members("age", period)
        # C.R.S. 39-22-119.5(3)(a)(III) counts the taxpayer's dependents under
        # 13. A return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents (IRC 152(b)(1)); only the
        # federal tax-liability condition is waived.
        filer_is_dependent = tax_unit.members.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        eligible_kid = (
            age < p.cdcc.low_income.child_age_threshold
        ) & ~filer_is_dependent
        eligible_kids = tax_unit.sum(eligible_kid)
        # tax_unit_childcare_expenses spreads the SPM unit's childcare
        # expenses evenly across children, so apportion the under-age share
        # over the number of children — not all CDCC qualifying individuals,
        # which can include disabled adults whose care is funded by the
        # separate care_expenses input.
        total_children = add(tax_unit, period, ["is_child"])
        eligible_kid_ratio = np.zeros_like(total_children, dtype=float)
        mask = total_children > 0
        eligible_kid_ratio[mask] = eligible_kids[mask] / total_children[mask]
        kid_expenses = care_expenses * eligible_kid_ratio
        capped_kid_expenses = min_(  # Line 3
            kid_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # calculate capped credit amount
        credit = p.cdcc.low_income.rate * capped_kid_expenses  # Line 11
        cap = p.cdcc.low_income.max_amount.calc(eligible_kids)  # Table A
        return min_(credit, cap)  # Line 12
