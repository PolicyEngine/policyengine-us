from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.tax.income.adjusted_gross_income.claim_of_right.nj_claim_of_right_repayment_category import (
    NJClaimOfRightRepaymentCategory,
)


class nj_claim_of_right_offset(Variable):
    value_type = float
    entity = Person
    label = "New Jersey claim of right repayment offset"
    unit = USD
    documentation = (
        "Reduction in a person's New Jersey gross income for a claim of "
        "right repayment. New Jersey applies a repayment against income of "
        "the same category in the year of repayment, and a category with a "
        "net negative amount is reported as zero, so the return's offset in "
        "each category is the smaller of its filers' repayments and their "
        "income in that category. Each spouse bears the offset in proportion "
        "to their own income in the category. New Jersey has no counterpart "
        "to the section 1341 credit, so the federal method does not matter."
    )
    definition_period = YEAR
    reference = (
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
        # TAM 2011-7, Claim of Right Repayment Refunds (IRC 1341)
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tams/tam7.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nj.tax.income.gross_income.claim_of_right_category_sources
        # Dependents' repayments and income belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        repayment = person("claim_of_right_repayment", period) * head_or_spouse
        category = person("nj_claim_of_right_repayment_category", period)
        offset = 0
        for value, sources in [
            (NJClaimOfRightRepaymentCategory.WAGES, p.wages),
            (NJClaimOfRightRepaymentCategory.INTEREST, p.interest),
            (NJClaimOfRightRepaymentCategory.DIVIDENDS, p.dividends),
            (NJClaimOfRightRepaymentCategory.GAMBLING_WINNINGS, p.gambling_winnings),
            (
                NJClaimOfRightRepaymentCategory.PENSIONS_AND_ANNUITIES,
                p.pensions_and_annuities,
            ),
            (NJClaimOfRightRepaymentCategory.ALIMONY, p.alimony),
        ]:
            income = max_(add(person, period, sources), 0) * head_or_spouse
            # The tax unit sums below are repeated for each member.
            return_income = person.tax_unit.sum(income)
            return_repayment = person.tax_unit.sum(repayment * (category == value))
            return_offset = min_(return_repayment, return_income)
            share = np.divide(
                income,
                return_income,
                out=np.zeros_like(income),
                where=return_income > 0,
            )
            offset = offset + share * return_offset
        return offset
