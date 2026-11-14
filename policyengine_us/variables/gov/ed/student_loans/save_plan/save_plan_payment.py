from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_borrower_income_helpers import (
    borrower_discretionary_income,
)


class save_plan_payment(Variable):
    value_type = float
    entity = Person
    label = "SAVE plan monthly payment (counterfactual)"
    documentation = (
        "Monthly payment a borrower would owe under the Saving on a Valuable "
        "Education (SAVE) plan as codified in 34 CFR 685.209(f)(1): the "
        "undergraduate and graduate rates weighted by the borrower's original "
        "balance, times discretionary income, prorated to the borrower's "
        "Direct Loans by income_driven_repayment_balance_share (which counts "
        "a joint filer's spouse's loans and both spouses' FFEL loans), then "
        "with the small payment adjustment. A borrower whom another taxpayer "
        "claims as a dependent pays on their own income "
        "(income_driven_repayment_dependent_adjusted_gross_income) above the "
        "plan's multiple of the poverty guideline for a family of one, with "
        "no spousal proration; the claiming taxpayer's income and loans do "
        "not enter. It assumes the borrower is "
        "enrolled in the plan and in active repayment, not in deferment, "
        "forbearance or default. Courts have blocked the SAVE plan, so this is a "
        "counterfactual: it is computed for any period and does not mean the "
        "plan is available. The pre-2023 REPAYE rule that counted a "
        "separately filing spouse's income is not modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2023-07-10/pdf/2023-13112.pdf#page=82",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans
        graduate_share = person("federal_student_loan_graduate_share", period.this_year)
        rates = p.save_plan.rate
        rate = (
            rates.undergraduate * (1 - graduate_share) + rates.graduate * graduate_share
        )
        # A head or spouse uses the tax unit's discretionary income. A
        # borrower claimed as a tax dependent uses their own income and a
        # family of one (685.209(b)(9), (b)(10), (e)(1)).
        discretionary_income = borrower_discretionary_income(
            person,
            period,
            parameters,
            "save_plan_discretionary_income",
            p.save_plan.fpg_exempt_rate,
        )
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        # Payments are set in whole cents. Rounding before the small payment
        # test keeps an exact $5.00 from falling below the threshold through
        # floating-point error.
        prorated_payment = np.round(rate * discretionary_income * balance_share, 2)
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            prorated_payment < small_payment.threshold,
            0,
            max_(prorated_payment, small_payment.minimum),
        )
        balance = person("federal_student_loan_balance", period.this_year)
        return min_(adjusted_payment, balance)
