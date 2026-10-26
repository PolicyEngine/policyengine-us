from policyengine_us.model_api import *


class repayment_assistance_plan_payment(Variable):
    value_type = float
    entity = Person
    label = "Repayment Assistance Plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Repayment Assistance "
        "Plan, after spousal proration and the final-payment cap. Payments in "
        "a year stop once they add up to the borrower's loan balance; interest "
        "accrual is not modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "repayment_assistance_plan_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=274",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(3)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.repayment_assistance_plan
        balance = person("federal_student_loan_balance", period.this_year)
        # Joint filers whose spouse also has eligible loans split the payment by
        # each spouse's share of the couple's eligible balance.
        eligible = person("repayment_assistance_plan_eligible", period)
        eligible_balance = where(eligible, balance, 0)
        couple_balance = person.tax_unit.sum(eligible_balance)
        balance_share = np.divide(
            eligible_balance,
            couple_balance,
            out=np.zeros_like(eligible_balance),
            where=couple_balance > 0,
        )
        applicable_payment = person.tax_unit(
            "repayment_assistance_plan_applicable_monthly_payment", period
        )
        monthly_payment = max_(applicable_payment * balance_share, p.minimum_payment)
        # Final payment: payments earlier in the year reduce the balance left
        # to repay, treating the monthly payment as constant within the year.
        prior_eligible_months = 0
        for month in period.this_year.get_subperiods(MONTH)[: period.start.month - 1]:
            prior_eligible_months += person("repayment_assistance_plan_eligible", month)
        remaining_balance = max_(balance - prior_eligible_months * monthly_payment, 0)
        return min_(monthly_payment, remaining_balance)
