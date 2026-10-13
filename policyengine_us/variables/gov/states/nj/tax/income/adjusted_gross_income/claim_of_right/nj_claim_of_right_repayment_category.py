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


# Amounts in a category's sources that New Jersey does not tax and subtracts
# from gross income separately, so a repayment cannot offset them.
CATEGORY_EXEMPT_SOURCES = {
    NJClaimOfRightRepaymentCategory.INTEREST: "interest",
}


def nj_claim_of_right_category_offset(person, period, parameters, category):
    """A person's share of the return's claim of right offset in one category.

    New Jersey applies a repayment against income of the same category in the
    year of repayment, and reports a category left negative as zero (N.J.S.A.
    54A:5-2; TAM 2011-7). A repayment first offsets the repayer's own taxable
    income in the category; on a joint return, whose category line combines
    both spouses, any excess offsets the other spouse's income in it. So the
    return's offset is the smaller of the filers' repayments of the category
    and their income in it, and no one's income in the category falls below
    zero. Dependents' repayments and income belong on their own returns.
    """
    gross_income = parameters(period).gov.states.nj.tax.income.gross_income
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    repaid_category = person("nj_claim_of_right_repayment_category", period)
    repayment = (
        person("claim_of_right_repayment", period)
        * head_or_spouse
        * (repaid_category == category)
    )
    sources = getattr(
        gross_income.claim_of_right_category_sources, CATEGORY_SOURCES[category]
    )
    income = add(person, period, sources)
    if category in CATEGORY_EXEMPT_SOURCES:
        exempt = getattr(
            gross_income.claim_of_right_category_exempt_sources,
            CATEGORY_EXEMPT_SOURCES[category],
        )
        income = income - add(person, period, exempt)
    income = max_(income, 0) * head_or_spouse
    own_offset = min_(repayment, income)
    # The tax unit sums below are repeated for each member.
    excess = person.tax_unit.sum(repayment - own_offset)
    remaining_income = income - own_offset
    return_remaining_income = person.tax_unit.sum(remaining_income)
    excess_offset = min_(excess, return_remaining_income)
    share = np.divide(
        remaining_income,
        return_remaining_income,
        out=np.zeros_like(remaining_income),
        where=return_remaining_income > 0,
    )
    return own_offset + share * excess_offset


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
