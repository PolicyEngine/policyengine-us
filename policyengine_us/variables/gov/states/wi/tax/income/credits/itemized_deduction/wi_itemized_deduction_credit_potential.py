from policyengine_us.model_api import *


class wi_itemized_deduction_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19",
        # Wis. Stat. 71.07(5)(a)
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=39",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Follow Form 1 Schedule 1, lines 1-4: medical expenses, interest,
        # gifts to charity and casualty losses, with no line for this deduction.
        # Wis. Stat. 71.07(5)(a)6 excludes repayments used for the state's
        # claim of right credit, and paragraph 7 excludes miscellaneous
        # itemized deductions (section 1341 is not one under IRC 67(b)(9)).
        # The statute is unclear for repayments not used for that credit;
        # Wisconsin's separate repayment relief is not modeled.
        wi_itmded = tax_unit("itemized_deductions_less_salt", period) - tax_unit(
            "claim_of_right_deduction", period
        )
        wi_stdded = tax_unit("wi_standard_deduction", period)
        excess_itmded = max_(0, wi_itmded - wi_stdded)
        p = parameters(period).gov.states.wi.tax.income
        return excess_itmded * p.credits.itemized_deduction.rate
