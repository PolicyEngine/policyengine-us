from policyengine_us.model_api import *


def amortized_monthly_payment(balance, annual_rate, number_of_payments):
    """Level monthly payment that repays `balance` in `number_of_payments`
    months at `annual_rate`, compounded monthly.

    The payment is balance x i / (1 - (1 + i) ^ -n), where i is the annual
    rate divided by 12 and n is the number of payments, or balance / n at a
    zero rate. `number_of_payments` can be a scalar or an array.
    """
    monthly_rate = annual_rate / MONTHS_IN_YEAR
    discount = 1 - (1 + monthly_rate) ** -number_of_payments
    payment_per_dollar = np.divide(
        monthly_rate,
        discount,
        out=np.ones_like(monthly_rate) / number_of_payments,
        where=monthly_rate > 0,
    )
    return balance * payment_per_dollar


def direct_standard_amortized_payment(person, period, parameters):
    """Level monthly payment on the person's Direct Loans over the 10-year
    standard repayment plan (34 CFR 685.208(b)(1)), before the plan minimum
    and the balance bound."""
    p = parameters(period).gov.ed.student_loans.standard_repayment
    balance = person("federal_student_loan_balance", period.this_year)
    annual_rate = person("federal_student_loan_interest_rate", period.this_year)
    number_of_payments = p.repayment_period * MONTHS_IN_YEAR
    return amortized_monthly_payment(balance, annual_rate, number_of_payments)


def parent_plus_standard_amortized_payment(person, period, parameters):
    """Level monthly payment on the person's parent PLUS loans under the
    standard repayment plan, before the plan minimum and the balance bound:
    10 years (34 CFR 685.208(b)(1)), or 10 to 30 years for a Direct
    Consolidation Loan that entered repayment on or after July 1, 2006
    (685.208(b)(2))."""
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
    return amortized_monthly_payment(balance, annual_rate, number_of_payments)
