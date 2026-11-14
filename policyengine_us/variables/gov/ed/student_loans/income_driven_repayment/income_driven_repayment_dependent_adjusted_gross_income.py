from policyengine_us.model_api import *


class income_driven_repayment_dependent_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Income-driven repayment adjusted gross income of a tax dependent"
    unit = USD
    documentation = (
        "Own income of a borrower whom another taxpayer claims as a dependent. "
        "It sets that borrower's payment under the Repayment Assistance Plan "
        "and the Income-Based Repayment, SAVE, Pay As You Earn and "
        "Income-Contingent Repayment plans. The law counts the borrower's "
        "income, and a spouse's on a joint return, not the income of the "
        "taxpayer who claims the borrower: 20 U.S.C. 1087e(q)(4)(A) for the "
        "Repayment Assistance Plan, and 34 CFR 685.209(b)(10) and (e)(1) for "
        "all five plans. Under 685.209(b)(10), income is the borrower's "
        "adjusted gross income as reported to the IRS or, without that, an "
        "amount based on alternative documentation of all forms of taxable "
        "income. The model does not compute a dependent's own return, so "
        "this defaults to dependent_gross_income: the dependent's gross "
        "income before any adjustments, with capital gains counted without "
        "netting losses and Social Security counted only where taxable. The "
        "default overstates adjusted gross income by the dependent's "
        "above-the-line deductions and capital losses. An explicit input "
        "overrides it, such as the adjusted gross income on the dependent's "
        "own most recent return. The default is zero for the head and "
        "spouse of a tax unit, whose payments use "
        "income_driven_repayment_adjusted_gross_income instead."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/20/1087e#q_4_A",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(10)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(ii)",
    )
    adds = ["dependent_gross_income"]
