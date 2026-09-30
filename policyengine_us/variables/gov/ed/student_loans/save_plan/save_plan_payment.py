from policyengine_us.model_api import *


class save_plan_payment(Variable):
    value_type = float
    entity = Person
    label = "SAVE plan monthly payment"
    documentation = (
        "Monthly payment a borrower would owe under the Saving on a Valuable "
        "Education (SAVE) plan as codified in 34 CFR 685.209(f)(1): the "
        "undergraduate and graduate rates weighted by the borrower's original "
        "balance, times discretionary income, prorated for joint filers whose "
        "spouse also has eligible loans, then with the small payment "
        "adjustment. Courts have blocked the SAVE plan, so this is a "
        "counterfactual: it is computed for any period and does not mean the "
        "plan is available. The pre-2023 REPAYE rule that counted a "
        "separately filing spouse's income is not modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "income_driven_repayment_eligible"
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2023-07-10/pdf/2023-13112.pdf#page=82",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans
        graduate_share = person("federal_student_loan_graduate_share", period.this_year)
        rates = p.save_plan.rate
        rate = (
            rates.undergraduate * (1 - graduate_share) + rates.graduate * graduate_share
        )
        discretionary_income = person.tax_unit("save_plan_discretionary_income", period)
        balance_share = person(
            "income_driven_repayment_balance_share", period.this_year
        )
        prorated_payment = rate * discretionary_income * balance_share
        small_payment = p.income_driven_repayment.small_payment
        adjusted_payment = where(
            prorated_payment < small_payment.threshold,
            0,
            max_(prorated_payment, small_payment.minimum),
        )
        balance = person("federal_student_loan_balance", period.this_year)
        return min_(adjusted_payment, balance)
