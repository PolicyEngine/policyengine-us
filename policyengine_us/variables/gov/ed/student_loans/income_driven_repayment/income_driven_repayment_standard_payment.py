from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class income_driven_repayment_standard_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-driven repayment 10-year standard payment cap"
    documentation = (
        "What the borrower would pay on the 10-year standard repayment plan "
        "based on the eligible loan balances and interest rates, the cap on "
        "Income-Based Repayment plan payments. Eligible loans are Direct and "
        "FFEL loans other than parent PLUS loans and excepted consolidation "
        "loans. A joint filer's spouse's eligible loans count too, so this is "
        "the sum over the head and spouse of the tax unit of each one's "
        "10-year standard payment on their federal_student_loan_balance plus "
        "federal_ffel_loan_balance, amortized at their own "
        "federal_student_loan_interest_rate. Each person's standard payment "
        "is at least the standard plan minimum and no more than their eligible "
        "balance. Married people filing separately are in separate tax units, "
        "so only the borrower's loans count. The cap uses the current balance, "
        "not the balance when the borrower began paying under the plan."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(3)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        person = tax_unit.members
        direct_balance = person("federal_student_loan_balance", period.this_year)
        ffel_balance = person("federal_ffel_loan_balance", period.this_year)
        eligible_balance = direct_balance + ffel_balance
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            eligible_balance, annual_rate, number_of_payments
        )
        # As in standard_repayment_payment, the minimum does not apply to a
        # final payment below it.
        standard_payment = min_(
            max_(amortized_payment, p.minimum_payment), eligible_balance
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        return tax_unit.sum(where(is_head_or_spouse, standard_payment, 0))
