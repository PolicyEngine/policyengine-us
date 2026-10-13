from policyengine_us.model_api import *


class NJClaimOfRightRepaymentCategory(Enum):
    WAGES = "Salaries, wages and other remuneration (category a)"
    INTEREST = "Interest (category e)"
    DIVIDENDS = "Dividends (category f)"
    GAMBLING_WINNINGS = "Gambling winnings (category g)"
    PENSIONS_AND_ANNUITIES = "Pensions, annuities and IRA withdrawals (category j)"
    ALIMONY = "Alimony and separate maintenance (category n)"
    OTHER = "Another category of New Jersey gross income (not offset in the model)"
    NOT_TAXED = "Income New Jersey did not tax when received"


# The parameter list of income sources for each category the model offsets.
CATEGORY_SOURCES = {
    NJClaimOfRightRepaymentCategory.WAGES: "wages",
    NJClaimOfRightRepaymentCategory.INTEREST: "interest",
    NJClaimOfRightRepaymentCategory.DIVIDENDS: "dividends",
    NJClaimOfRightRepaymentCategory.GAMBLING_WINNINGS: "gambling_winnings",
    NJClaimOfRightRepaymentCategory.PENSIONS_AND_ANNUITIES: "pensions_and_annuities",
    NJClaimOfRightRepaymentCategory.ALIMONY: "alimony",
}


def nj_claim_of_right_category_offset(person, period, parameters, category):
    """A person's share of the return's claim of right offset in one category.

    New Jersey applies a repayment against income of the same category in the
    year of repayment, and reports a category left negative as zero (N.J.S.A.
    54A:5-2; TAM 2011-7). So the return's offset in a category is the smaller
    of the head's and spouse's repayments of that category and their income in
    it. Each bears it in proportion to their own income in the category, so
    no one's income in the category falls below zero. Dependents' repayments
    and income belong on their own returns.
    """
    p = parameters(
        period
    ).gov.states.nj.tax.income.gross_income.claim_of_right_category_sources
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    repayment = person("claim_of_right_repayment", period) * head_or_spouse
    repaid_category = person("nj_claim_of_right_repayment_category", period)
    sources = getattr(p, CATEGORY_SOURCES[category])
    income = max_(add(person, period, sources), 0) * head_or_spouse
    # The tax unit sums below are repeated for each member.
    return_income = person.tax_unit.sum(income)
    return_repayment = person.tax_unit.sum(repayment * (repaid_category == category))
    return_offset = min_(return_repayment, return_income)
    share = np.divide(
        income,
        return_income,
        out=np.zeros_like(income),
        where=return_income > 0,
    )
    return share * return_offset


class nj_claim_of_right_repayment_category(Variable):
    value_type = Enum
    possible_values = NJClaimOfRightRepaymentCategory
    default_value = NJClaimOfRightRepaymentCategory.WAGES
    entity = Person
    label = "New Jersey gross income category of a claim of right repayment"
    documentation = (
        "The New Jersey gross income category (N.J.S.A. 54A:5-1) of the "
        "income repaid in claim_of_right_repayment. New Jersey offsets the "
        "repayment only against income of the same category in the year of "
        "repayment. NOT_TAXED is income New Jersey did not tax when "
        "received, such as unemployment compensation or Social Security "
        "benefits. OTHER is a category the model does not offset, such as "
        "prizes and awards or income from estates and trusts. Defaults to "
        "wages, the category of TAM 2011-7's example."
    )
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tams/tam7.pdf",
    )
    defined_for = StateCode.NJ
