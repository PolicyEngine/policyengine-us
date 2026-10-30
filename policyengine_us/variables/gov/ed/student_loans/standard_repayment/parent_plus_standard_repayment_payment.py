from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class parent_plus_standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Parent PLUS standard repayment plan monthly payment"
    documentation = (
        "Fixed monthly payment that repays the person's parent PLUS loans "
        "(federal_parent_plus_loan_balance) under the standard repayment "
        "plan. Unconsolidated parent PLUS loans repay over 10 years. A Direct "
        "Consolidation Loan that repaid them and entered repayment on or after "
        "July 1, 2006 (federal_parent_plus_loan_is_consolidated) repays over "
        "10 to 30 years, set by the total of the consolidation loan and the "
        "borrower's other education loans, which count up to the amount of "
        "the consolidation loan. The current balances stand in for the "
        "balances when the consolidation loan entered repayment, and the "
        "other education loans are the person's federal_student_loan_balance "
        "and federal_ffel_loan_balance; private education loans are not "
        "modeled. The balance is amortized at the person's "
        "federal_student_loan_interest_rate, a single rate for all of their "
        "federal loans, and the payment is at least the plan minimum and no "
        "more than the balance. It assumes the borrower is in active "
        "repayment. This is separate from standard_repayment_payment, so the "
        "income-driven repayment caps stay on the loans those plans can "
        "repay. A borrower with a Direct Loan made on or after July 1, 2026 "
        "cannot use this plan: the tiered standard plan "
        "(tiered_standard_repayment_payment) repays their parent PLUS loans, "
        "so this is zero for them. The flag is yearly, so a loan made in the "
        "second half of 2026 moves all of 2026 to the tiered plan. Repayment "
        "of consolidated parent PLUS loans under the Income-Contingent "
        "Repayment plan is not modeled."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/20/1087e#d_1_A",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.220#p-685.220(i)(2)(ii)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        balance = person("federal_parent_plus_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        # 685.208(b)(2)(iii) and 685.220(i)(2)(ii), (i)(3)(i): a consolidation
        # loan's term follows its amount plus the borrower's other education
        # loans, counted up to the consolidation loan's amount.
        other_loans = add(
            person,
            period.this_year,
            ["federal_student_loan_balance", "federal_ffel_loan_balance"],
        )
        consolidation_total = balance + min_(other_loans, balance)
        is_consolidated = person(
            "federal_parent_plus_loan_is_consolidated", period.this_year
        )
        repayment_period = where(
            is_consolidated,
            p.consolidation_repayment_period.calc(consolidation_total),
            p.repayment_period,
        )
        number_of_payments = repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            balance, annual_rate, number_of_payments
        )
        # As in standard_repayment_payment, the minimum does not apply to a
        # final payment below it.
        payment = min_(max_(amortized_payment, p.minimum_payment), balance)
        # 20 U.S.C. 1087e(d)(1) and (d)(7)(A) and 34 CFR 685.208(b)(1)-(2)
        # limit this plan to borrowers with no Direct Loan made on or after
        # July 1, 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
