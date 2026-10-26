from policyengine_us.model_api import *


class federal_ffel_loan_balance(Variable):
    value_type = float
    entity = Person
    label = "Federal Family Education Loan balance"
    documentation = (
        "Outstanding principal and interest on the person's Federal Family "
        "Education Loan (FFEL) Program loans that are eligible loans under 34 "
        "CFR 685.209(b)(5)(ii): every FFEL loan except Federal PLUS Loans made "
        "to parents and excepted consolidation loans. The Direct Loan "
        "income-driven repayment plans do not repay these loans, but the "
        "balance enters the spousal and FFEL adjustments of 685.209(g)(1) and "
        "(g)(3) and the 10-year standard payment cap of the Income-Based "
        "Repayment and Pay As You Earn plans. FFEL loans consolidated into a "
        "Direct Consolidation "
        "Loan belong in federal_student_loan_balance instead. This is the "
        "opening balance for the year. Later years hold it at its dataset "
        "(input) value, with no price or income uprating and no repayment "
        "roll-forward."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(5)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(6)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)(ii)",
    )
