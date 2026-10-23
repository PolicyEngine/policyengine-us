from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class income_contingent_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Income-Contingent Repayment plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Income-Contingent "
        "Repayment plan: the lesser of the 12-year fixed payment on the "
        "borrower's balance times the income percentage factor, and the plan "
        "rate times discretionary income, then with the plan's minimum "
        "payment. The fixed payment amortizes the current balance at the "
        "loans' interest rate, not the balance when the borrower entered the "
        "plan. Joint filers use the couple's combined income, and each "
        "spouse's payment uses only their own balance; the payment is not "
        "prorated, because 34 CFR 685.209(g)(1) adjusts only the other plans. "
        "Married borrowers who elect to repay jointly (685.209(f)(4)(ii)) are "
        "not modeled. A borrower with a Direct Loan made on or after July 1, "
        "2026 cannot use the plan and owes nothing under it. The other limits "
        "on who can repay under the plan are not modeled: repaying under the "
        "plan on July 1, 2024, and the plan's end on June 30, 2028 "
        "(685.209(c)(5)). Consolidation loans that repaid Parent PLUS loans, "
        "which only this plan can repay, are not included."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(4)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(2)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=123",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-09/pdf/2026-11540.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.income_contingent_repayment
        balance = person("federal_student_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        fixed_payment = amortized_monthly_payment(
            balance, annual_rate, number_of_payments
        )
        factor = person.tax_unit(
            "income_contingent_repayment_income_percentage_factor", period
        )
        discretionary_income = person.tax_unit(
            "income_contingent_repayment_discretionary_income", period
        )
        income_payment = p.rate * discretionary_income
        # Payments are set in whole cents. Rounding before the minimum keeps
        # floating-point residue from turning a $0 payment into the $5
        # minimum.
        calculated_payment = np.round(min_(fixed_payment * factor, income_payment), 2)
        # A calculated payment above zero and at or below the minimum is raised
        # to the minimum.
        adjusted_payment = where(
            calculated_payment > 0,
            max_(calculated_payment, p.minimum_payment),
            0,
        )
        payment = min_(adjusted_payment, balance)
        # 20 U.S.C. 1087e(d)(6)-(7) and 34 CFR 685.209(c)(5)(i)(C), (d)(5)
        # limit the plan to borrowers with no Direct Loan made on or after
        # July 1, 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
