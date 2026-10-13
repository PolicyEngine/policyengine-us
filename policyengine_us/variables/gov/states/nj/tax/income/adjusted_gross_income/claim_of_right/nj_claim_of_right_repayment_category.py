from policyengine_us.model_api import *


class NJClaimOfRightRepaymentCategory(Enum):
    WAGES = "Salaries, wages and other remuneration (category a)"
    INTEREST = "Interest (category e)"
    DIVIDENDS = "Dividends (category f)"
    GAMBLING_WINNINGS = "Gambling winnings (category g)"
    PENSIONS_AND_ANNUITIES = "Pensions, annuities and IRA withdrawals (category j)"
    ALIMONY = "Alimony and separate maintenance (category n)"
    NOT_TAXED = "Income New Jersey did not tax when received"


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
        "benefits. Defaults to wages."
    )
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tams/tam7.pdf",
    )
    defined_for = StateCode.NJ
