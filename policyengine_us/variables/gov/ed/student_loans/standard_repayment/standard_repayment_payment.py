from policyengine_us.model_api import *


class standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Standard repayment plan monthly payment"
    documentation = (
        "Fixed monthly payment that repays the person's federal student loan "
        "balance over the 10-year standard repayment plan at the loans' "
        "interest rate, at least the plan minimum and no more than the "
        "balance. The payment amortizes the current balance, not the balance "
        "when the loans entered repayment. Loans made on or after July 1, "
        "2026, which repay under the tiered standard plan, are not modeled."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        balance = person("federal_student_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        monthly_rate = annual_rate / MONTHS_IN_YEAR
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        # Level payment that repays the balance in n months at monthly rate i:
        # balance x i / (1 - (1 + i) ^ -n), or balance / n at a zero rate.
        discount = 1 - (1 + monthly_rate) ** -number_of_payments
        payment_per_dollar = np.divide(
            monthly_rate,
            discount,
            out=np.ones_like(monthly_rate) / number_of_payments,
            where=monthly_rate > 0,
        )
        amortized_payment = balance * payment_per_dollar
        # The minimum does not apply to a final payment below it.
        return min_(max_(amortized_payment, p.minimum_payment), balance)
