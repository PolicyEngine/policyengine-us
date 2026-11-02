from policyengine_us.model_api import *


class pay_as_you_earn_payment(Variable):
    value_type = float
    entity = Person
    label = "Pay As You Earn plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Pay As You Earn plan, "
        "assuming the borrower is enrolled in the plan and in active "
        "repayment, not in deferment, forbearance or default. The plan rate "
        "times discretionary income is prorated to the borrower's Direct "
        "Loans (income_driven_repayment_balance_share, which for joint filers "
        "divides by both spouses' Direct and FFEL loans) and capped at the "
        "Direct Loan part of the borrower's own 10-year standard payment "
        "(income_driven_repayment_standard_payment on their Direct and FFEL "
        "loans at their own interest rate, times their Direct share of those "
        "loans). The result is rounded to the cent, given the small payment "
        "adjustment and capped at the borrower's Direct Loan balance. Each "
        "spouse's cap covers only their own loans. As with the Income-Based "
        "Repayment plan, the cap uses the current balance, not the balance "
        "when the borrower entered the plan. A borrower with a Direct Loan "
        "made on or after July 1, 2026 cannot use the plan and owes nothing "
        "under it. The other limits on who can repay under the plan are not "
        "modeled: being a new borrower under 34 CFR 685.209(b)(13)(i), "
        "repaying under the plan on July 1, 2024, and the plan's end on June "
        "30, 2028 (685.209(c)(4)). The prorated payment is rounded to the "
        "cent before the small payment adjustment, a modeling choice: a "
        "calculated payment just under $5, such as $4.996, rounds to $5.00 "
        "and becomes $10 rather than $0 under 685.209(g)(1)(iii), which sets "
        "a payment of less than $5 to $0."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(4)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=123",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans
        discretionary_income = person.tax_unit(
            "pay_as_you_earn_discretionary_income", period
        )
        # 685.209(g)(1)(i)-(ii) prorate the income-based amount to the
        # borrower's Direct Loans. 685.209(f)(2)(ii), as in 20 U.S.C.
        # 1098e(b)(6)(A) for the Income-Based Repayment plan, caps the payment
        # on all of the borrower's eligible loans at their own 10-year standard
        # payment; the Direct Loans carry the (g)(1)(ii) part of that cap.
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        balance = person("federal_student_loan_balance", period.this_year)
        eligible_balance = balance + person(
            "federal_ffel_loan_balance", period.this_year
        )
        direct_fraction = np.divide(
            balance,
            eligible_balance,
            out=np.zeros_like(balance),
            where=eligible_balance > 0,
        )
        standard_payment = person("income_driven_repayment_standard_payment", period)
        # Payments are set in whole cents. Rounding before the small payment
        # test keeps an exact $5.00 from falling below the threshold through
        # floating-point error. It also lifts an amount within half a cent
        # below $5 to $5.00, a modeling choice described in the documentation.
        prorated_payment = np.round(
            min_(
                p.pay_as_you_earn.rate * discretionary_income * balance_share,
                standard_payment * direct_fraction,
            ),
            2,
        )
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            prorated_payment < small_payment.threshold,
            0,
            max_(prorated_payment, small_payment.minimum),
        )
        payment = min_(adjusted_payment, balance)
        # 20 U.S.C. 1087e(d)(1) and (d)(7)(A) and 34 CFR 685.209(c)(4)(v),
        # (d)(5) limit the plan to borrowers with no Direct Loan made on or
        # after July 1, 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
