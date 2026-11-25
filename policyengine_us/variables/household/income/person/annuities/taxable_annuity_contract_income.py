from policyengine_us.model_api import *

ANNUITY_CONTRACT_SLOTS = 3


class taxable_annuity_contract_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable income from annuity contracts outside qualified plans"
    documentation = (
        "Per contract: annuity payments less the exclusion ratio part "
        "(investment over expected return), with the exclusion stopping once "
        "the investment is recovered for starting dates after 1986; plus "
        "withdrawals taxed income-first, after any pre-August 14, 1982 "
        "investment is recovered."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#b",
        "https://www.law.cornell.edu/uscode/text/26/72#e",
        "https://www.irs.gov/publications/p939",
    )

    def formula(person, period, parameters):
        total = 0
        for slot in range(1, ANNUITY_CONTRACT_SLOTS + 1):

            def v(field):
                return person(f"annuity_contract_{slot}_{field}", period)

            payments = max_(0, v("annuity_payments"))
            investment = max_(0, v("investment_in_contract"))
            share = v("annuitized_share")
            share = where((share <= 0) & (payments > 0), 1, np.clip(share, 0, 1))
            annuity_investment = investment * share
            expected = max_(0, v("expected_return"))
            ratio = np.clip(
                np.divide(
                    annuity_investment,
                    expected,
                    out=np.zeros_like(expected),
                    where=expected > 0,
                ),
                0,
                1,
            )
            excluded = payments * ratio
            unrecovered = max_(
                0, annuity_investment - max_(0, v("investment_recovered"))
            )
            excluded = where(
                v("starting_date_before_1987"), excluded, min_(excluded, unrecovered)
            )
            annuity_taxable = payments - excluded
            # Withdrawals: tax-free up to remaining pre-August 14, 1982
            # investment, then income first up to the gain in the contract.
            withdrawals = max_(0, v("withdrawals"))
            pre_1982 = max_(0, v("pre_august_1982_investment"))
            after_grandfather = max_(0, withdrawals - pre_1982)
            deferred_investment = max_(0, investment - annuity_investment)
            gain = max_(0, v("cash_value") - deferred_investment)
            withdrawal_taxable = min_(after_grandfather, gain)
            total = total + annuity_taxable + withdrawal_taxable
        return total
