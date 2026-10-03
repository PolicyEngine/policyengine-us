from policyengine_us.model_api import *


class federal_student_loan_balance(Variable):
    value_type = float
    entity = Person
    label = "Federal student loan balance"
    documentation = (
        "Outstanding principal and interest on the person's William D. Ford "
        "Federal Direct Loans that can be repaid under the Repayment Assistance "
        "Plan: Direct Subsidized, Direct Unsubsidized, Direct PLUS Loans made to "
        "graduate or professional students, and Direct Consolidation Loans that "
        "are not excepted consolidation loans. Excludes Parent PLUS loans and "
        "consolidation loans that repaid them (see "
        "federal_parent_plus_loan_balance), and FFEL or Perkins loans that have "
        "not been consolidated into a Direct Consolidation Loan."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(6)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(4)",
    )
