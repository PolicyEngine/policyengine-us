from policyengine_us.model_api import *


class is_income_based_repayment_new_borrower(Variable):
    value_type = bool
    entity = Person
    label = "New borrower under the Income-Based Repayment plan"
    documentation = (
        "The person had no outstanding Direct Loan or FFEL balance when they "
        "borrowed on or after July 1, 2014, and has no loan made on or after "
        "July 1, 2026."
    )
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1098e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(13)(ii)",
    )
