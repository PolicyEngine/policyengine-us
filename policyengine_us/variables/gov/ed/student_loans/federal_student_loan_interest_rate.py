from policyengine_us.model_api import *


class federal_student_loan_interest_rate(Variable):
    value_type = float
    entity = Person
    label = "Federal student loan interest rate"
    documentation = (
        "Annual interest rate on the loans in federal_student_loan_balance, "
        "weighted by balance. Used to amortize the balance under the "
        "standard repayment plan. As a simplification, one rate stands in for "
        "all of the person's federal loans: the Income-Based Repayment and "
        "Pay As You Earn plans' standard payment cap also applies it to the "
        "person's federal_ffel_loan_balance, and "
        "parent_plus_standard_repayment_payment to their "
        "federal_parent_plus_loan_balance, although FFEL and parent PLUS "
        "loans carry their own rates (34 CFR 682.202(a), 685.202(a))."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.202#p-685.202(a)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(a)",
        "https://www.ecfr.gov/current/title-34/section-682.202#p-682.202(a)",
    )
