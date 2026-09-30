from policyengine_us.model_api import *


class income_based_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Income-Based Repayment plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Income-Based Repayment "
        "plan: the plan rate times discretionary income, prorated for joint "
        "filers whose spouse also has eligible loans, capped at the 10-year "
        "standard payment, then with the small payment adjustment. The cap "
        "uses the current balance, not the balance when the borrower entered "
        "the plan. Prorating before capping each spouse at their own standard "
        "payment matches capping the couple at their combined standard "
        "payment when both spouses' loans carry the same interest rate. The "
        "bar on borrowers with a loan made on or after July 1, 2026 is not "
        "modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1098e&num=0&edition=prelim",
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
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        prorated_payment = rate * discretionary_income * balance_share
        standard_payment = person("standard_repayment_payment", period)
        capped_payment = min_(prorated_payment, standard_payment)
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            capped_payment < small_payment.threshold,
            0,
            max_(capped_payment, small_payment.minimum),
        )
        balance = person("federal_student_loan_balance", period.this_year)
        return min_(adjusted_payment, balance)
