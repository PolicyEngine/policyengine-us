from policyengine_us.model_api import *


class federal_student_loan_interest_rate(Variable):
    value_type = float
    entity = Person
    label = "Federal student loan interest rate"
    documentation = (
        "Annual interest rate on the loans in federal_student_loan_balance, "
        "weighted by balance. Used to amortize the balance under the "
        "standard repayment plan."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.202#p-685.202(a)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(a)",
    )
