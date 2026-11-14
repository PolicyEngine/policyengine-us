from policyengine_us.model_api import *


class income_driven_repayment_balance_share(Variable):
    value_type = float
    entity = Person
    label = "Income-driven repayment share of the couple's eligible balance"
    documentation = (
        "Share of the Income-Based Repayment, SAVE or Pay As You Earn plan "
        "payment that the person owes on their Direct Loans. 34 CFR "
        "685.209(g)(1)(i) first "
        "prorates the payment by the person's share of the eligible loans of "
        "the head and spouse of their tax unit, where eligible loans are "
        "Direct and FFEL loans (federal_student_loan_balance plus "
        "federal_ffel_loan_balance). 685.209(g)(1)(ii) then multiplies by the "
        "Direct Loan share of the person's own eligible loans, since these "
        "plans do not repay FFEL loans. The product is the person's Direct "
        "Loan balance divided by the couple's combined Direct and FFEL "
        "balance. Married people filing separately are in separate tax units, "
        "so only their own loans count. A borrower claimed as a tax dependent "
        "is not the spouse of anyone in the unit, so only (g)(1)(ii) applies: "
        "their share is their Direct Loan balance divided by their own Direct "
        "and FFEL balance, and their loans stay out of the head and spouse's "
        "shares. Under the Income-Based Repayment and "
        "Pay As You Earn plans the share multiplies the lesser of the "
        "income-based amount and the borrower's own 10-year standard payment, "
        "since (g)(1) adjusts the amount calculated under (f)(2) and (f)(3)."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)(ii)",
    )

    def formula(person, period, parameters):
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        direct_balance = person("federal_student_loan_balance", period)
        ffel_balance = person("federal_ffel_loan_balance", period)
        eligible_balance = direct_balance + ffel_balance
        # (g)(1)(i) x (g)(1)(ii):
        # (own Direct + own FFEL) / couple's (Direct + FFEL)
        #   x own Direct / (own Direct + own FFEL)
        # = own Direct / couple's (Direct + FFEL).
        couple_balance = person.tax_unit.sum(
            where(is_head_or_spouse, eligible_balance, 0)
        )
        # 685.209(e)(2)(i) adds only a spouse's loans, so a borrower claimed as
        # a tax dependent is prorated by (g)(1)(ii) alone.
        proration_balance = where(is_head_or_spouse, couple_balance, eligible_balance)
        return np.divide(
            direct_balance,
            proration_balance,
            out=np.zeros_like(direct_balance),
            where=proration_balance > 0,
        )
