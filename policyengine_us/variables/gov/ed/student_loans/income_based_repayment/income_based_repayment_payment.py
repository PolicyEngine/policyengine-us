from policyengine_us.model_api import *


class income_based_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Income-Based Repayment plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Income-Based Repayment "
        "plan, assuming the borrower is enrolled in the plan and in active "
        "repayment, not in deferment, forbearance or default. The payment is "
        "the lesser of the borrower's plan rate times discretionary income "
        "and the 10-year standard payment on the eligible loans "
        "(income_driven_repayment_standard_payment, which for joint filers "
        "covers both spouses' Direct and FFEL loans). That amount is prorated "
        "to the borrower's Direct Loans (income_driven_repayment_balance_share), "
        "rounded to the cent, given the small payment adjustment and capped at "
        "the borrower's Direct Loan balance. Spouses keep their own rates, so a "
        "new borrower pays 10 percent and the other spouse 15 percent of the "
        "same discretionary income before the cap and proration. The cap uses "
        "the current balance, not the balance when the borrower entered the "
        "plan. The bar on borrowers with a loan made on or after July 1, 2026 "
        "is not modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1098e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(3)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
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
        # 685.209(f)(2)-(3): the lesser of the income-based amount and the
        # standard payment on all of the couple's eligible loans, then the
        # (g)(1)(i)-(ii) proration to the borrower's Direct Loans.
        standard_payment = person.tax_unit(
            "income_driven_repayment_standard_payment", period
        )
        capped_payment = min_(rate * discretionary_income, standard_payment)
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        # Payments are set in whole cents. Rounding before the small payment
        # test keeps an exact $5.00 from falling below the threshold through
        # floating-point error (e.g. 15% x $400 / 12).
        prorated_payment = np.round(capped_payment * balance_share, 2)
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            prorated_payment < small_payment.threshold,
            0,
            max_(prorated_payment, small_payment.minimum),
        )
        balance = person("federal_student_loan_balance", period.this_year)
        return min_(adjusted_payment, balance)
