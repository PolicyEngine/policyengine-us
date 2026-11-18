from policyengine_us.model_api import *


class has_federal_student_loan_made_on_or_after_2026_07_01(Variable):
    value_type = bool
    entity = Person
    label = "Has a federal student loan made on or after July 1, 2026"
    documentation = (
        "The person received a William D. Ford Federal Direct Loan made on or "
        "after July 1, 2026. Such a borrower can repay all of their Direct "
        "Loans only under the Repayment Assistance Plan or the tiered "
        "standard repayment plan, so the Income-Based Repayment, Pay As You "
        "Earn, Income-Contingent Repayment and 10-year standard plans are "
        "unavailable. Set it only for years from 2026 on, after the loan is "
        "made."
    )
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=268",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(8)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(c)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(5)",
    )
