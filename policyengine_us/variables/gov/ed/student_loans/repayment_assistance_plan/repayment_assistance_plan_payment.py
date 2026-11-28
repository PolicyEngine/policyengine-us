from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_borrower_income_helpers import (
    dependent_borrower_repayment_assistance_plan_applicable_payment,
)


class repayment_assistance_plan_payment(Variable):
    value_type = float
    entity = Person
    label = "Repayment Assistance Plan monthly payment"
    documentation = (
        "Monthly payment owed by a borrower under the Repayment Assistance "
        "Plan, after spousal proration and the final-payment cap, assuming the "
        "borrower is enrolled in the plan and in active repayment, not in "
        "deferment, forbearance or default. Joint filers owe the applicable "
        "monthly payment times their share of the couple's eligible loans, "
        "which per 34 CFR 685.209(b)(5) and (g)(3)(i) are Direct and FFEL "
        "loans (federal_student_loan_balance plus federal_ffel_loan_balance), "
        "and at least the minimum payment. The plan cannot repay FFEL loans "
        "(685.209(d)(4)), and (g)(3) has no FFEL adjustment like (g)(1)(ii), "
        "so a borrower's own FFEL loans raise their share of the payment on "
        "their Direct Loans. The proposed rule (91 FR 4284-85) and the final "
        "rule's preamble (91 FR 23838) copied the Income-Based Repayment "
        "plan's (g)(1)(i) proration 'to provide consistency with IBR' without "
        "discussing FFEL loans, so the code follows the text of (g)(3)(i). "
        "A borrower whom another taxpayer claims as a dependent pays on their "
        "own income (income_driven_repayment_dependent_adjusted_gross_income): "
        "the base payment on that income divided by 12, with no dependent "
        "reduction and no spousal proration, and at least the minimum "
        "payment. The claiming taxpayer's income and loans do not enter, and "
        "the dependent still counts toward the claiming taxpayer's dependent "
        "reduction. "
        "Payments in a year stop once they add up to the "
        "borrower's opening Direct Loan balance; interest accrual is not "
        "modeled."
    )
    unit = USD
    definition_period = MONTH
    defined_for = "repayment_assistance_plan_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=274",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(3)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=71",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.repayment_assistance_plan
        balance = person("federal_student_loan_balance", period.this_year)
        # Joint filers split the payment by each spouse's share of the couple's
        # eligible Direct and FFEL loans (685.209(b)(5), (g)(3)(i)).
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        ffel_balance = person("federal_ffel_loan_balance", period.this_year)
        eligible_balance = balance + ffel_balance
        couple_balance = person.tax_unit.sum(
            where(is_head_or_spouse, eligible_balance, 0)
        )
        # 685.209(e)(2)(i) adds only a spouse's loans, so a borrower claimed as
        # a tax dependent owes their whole applicable payment.
        proration_balance = where(is_head_or_spouse, couple_balance, eligible_balance)
        balance_share = np.divide(
            eligible_balance,
            proration_balance,
            out=np.zeros_like(eligible_balance),
            where=proration_balance > 0,
        )
        # A head or spouse uses the tax unit's applicable payment. A borrower
        # claimed as a tax dependent uses their own income, with no dependent
        # reduction (20 U.S.C. 1087e(q)(4)(A); 685.209(e)(1)(i)).
        applicable_payment = where(
            is_head_or_spouse,
            person.tax_unit(
                "repayment_assistance_plan_applicable_monthly_payment", period
            ),
            dependent_borrower_repayment_assistance_plan_applicable_payment(
                person, period, parameters
            ),
        )
        monthly_payment = max_(applicable_payment * balance_share, p.minimum_payment)
        # Final payment: payments earlier in the year reduce the balance left
        # to repay, treating the monthly payment as constant within the year.
        prior_eligible_months = 0
        for month in period.this_year.get_subperiods(MONTH)[: period.start.month - 1]:
            prior_eligible_months += person("repayment_assistance_plan_eligible", month)
        remaining_balance = max_(balance - prior_eligible_months * monthly_payment, 0)
        return min_(monthly_payment, remaining_balance)
