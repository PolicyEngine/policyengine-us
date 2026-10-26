from policyengine_us.model_api import *


class income_driven_repayment_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-driven repayment adjusted gross income"
    unit = USD
    documentation = (
        "Adjusted gross income on the most recent federal income tax return "
        "available when the Department of Education sets the monthly payment, "
        "which the Repayment Assistance Plan and the Income-Based Repayment, "
        "SAVE, Pay As You Earn and Income-Contingent Repayment plans use as "
        "income: 20 U.S.C. 1087e(q)(4)(A) takes adjusted gross "
        "income 'for the most recent taxable year'. That is usually the prior "
        "year's return, or documentation of current income the borrower "
        "supplies instead. Household and microsimulation inputs usually cover "
        "a single year, so reading the prior year would return zero income; "
        "when not provided, this defaults to the current year's adjusted "
        "gross income. An explicit input overrides it."
    )
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(l)(4)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(l)(6)",
    )
    adds = ["adjusted_gross_income"]
