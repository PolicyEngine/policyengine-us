from policyengine_us.model_api import *


class pay_as_you_earn_payment(Variable):
    value_type = float
    entity = Person
    label = "Pay As You Earn plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Pay As You Earn plan: "
        "the plan rate times discretionary income, prorated for joint filers "
        "whose spouse also has eligible loans, capped at the 10-year standard "
        "payment, then with the small payment adjustment. As with the "
        "Income-Based Repayment plan, the cap uses the current balance, not "
        "the balance when the borrower entered the plan. A borrower with a "
        "Direct Loan made on or after July 1, 2026 cannot use the plan and "
        "owes nothing under it. The other limits on who can repay under the "
        "plan are not modeled: being a new borrower under 34 CFR "
        "685.209(b)(13)(i), repaying under the plan on July 1, 2024, and the "
        "plan's end on June 30, 2028 (685.209(c)(4))."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(4)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=123",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans
        discretionary_income = person.tax_unit(
            "pay_as_you_earn_discretionary_income", period
        )
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        prorated_payment = p.pay_as_you_earn.rate * discretionary_income * balance_share
        standard_payment = person("standard_repayment_payment", period)
        # Payments are set in whole cents. Rounding before the small payment
        # test keeps an exact $5.00 from falling below the threshold through
        # floating-point error.
        capped_payment = np.round(min_(prorated_payment, standard_payment), 2)
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            capped_payment < small_payment.threshold,
            0,
            max_(capped_payment, small_payment.minimum),
        )
        balance = person("federal_student_loan_balance", period.this_year)
        payment = min_(adjusted_payment, balance)
        # 20 U.S.C. 1087e(d)(6)-(7) and 34 CFR 685.209(c)(4)(v), (d)(5) limit
        # the plan to borrowers with no Direct Loan made on or after July 1,
        # 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
