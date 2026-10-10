from policyengine_us.model_api import *


class federal_parent_plus_loan_balance(Variable):
    value_type = float
    entity = Person
    label = "Federal Parent PLUS loan balance"
    documentation = (
        "Outstanding principal and interest on Federal Direct PLUS Loans the "
        "person borrowed as a parent on behalf of a dependent student, and on "
        "Direct Consolidation Loans that repaid such loans. These excepted "
        "loans cannot be repaid under the Repayment Assistance Plan."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(7)",
    )
