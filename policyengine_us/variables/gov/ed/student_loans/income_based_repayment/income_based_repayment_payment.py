from policyengine_us.model_api import *


class income_based_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Income-Based Repayment plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Income-Based Repayment "
        "plan, assuming the borrower is enrolled in the plan and in active "
        "repayment, not in deferment, forbearance or default. The borrower's "
        "plan rate times discretionary income is prorated to their Direct "
        "Loans (income_driven_repayment_balance_share, which for joint filers "
        "divides by both spouses' Direct and FFEL loans) and capped at the "
        "Direct Loan part of the borrower's own 10-year standard payment "
        "(income_driven_repayment_standard_payment on their Direct and FFEL "
        "loans, times their Direct share of those loans). The result is "
        "rounded to the cent, given the small payment adjustment and capped "
        "at the borrower's Direct Loan balance. Spouses keep their own rates, "
        "so a new borrower pays 10 percent and the other spouse 15 percent of "
        "the same discretionary income before proration, and each spouse's "
        "cap covers only their own loans. The cap uses the current balance, "
        "not the balance when the borrower entered the plan. The prorated "
        "payment is rounded to the cent before the small payment adjustment, "
        "a modeling choice: a calculated payment just under $5, such as "
        "$4.996, rounds to $5.00 and becomes $10 rather than $0 under 34 CFR "
        "685.209(g)(1)(iii), which sets a payment of less than $5 to $0. A "
        "borrower with a Direct Loan made on or after July 1, 2026 cannot use "
        "the plan and owes nothing under it."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://www.law.cornell.edu/uscode/text/20/1098e#b_6_A",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(3)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(5)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans
        new_borrower = person(
            "is_income_based_repayment_new_borrower", period.this_year
        )
        rate = where(
            new_borrower,
            p.income_based_repayment.new_borrower_rate,
            p.income_based_repayment.rate,
        )
        discretionary_income = person.tax_unit(
            "income_based_repayment_discretionary_income", period
        )
        # 685.209(g)(1)(i)-(ii) prorate the income-based amount to the
        # borrower's Direct Loans. 20 U.S.C. 1098e(b)(6)(A) and 685.209(f)(2)(ii),
        # (f)(3)(ii) cap the payment on all of the borrower's eligible loans at
        # their own 10-year standard payment; the Direct Loans carry the
        # (g)(1)(ii) part of that cap.
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
        # floating-point error (e.g. 15% x $400 / 12). It also lifts an amount
        # within half a cent below $5 to $5.00, a modeling choice described in
        # the documentation.
        prorated_payment = np.round(
            min_(
                rate * discretionary_income * balance_share,
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
        # 20 U.S.C. 1087e(d)(1) and (d)(7)(A) and 34 CFR 685.209(d)(5) limit
        # the plan to borrowers with no Direct Loan made on or after July 1,
        # 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
