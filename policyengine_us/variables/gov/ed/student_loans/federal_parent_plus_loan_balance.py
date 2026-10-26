from policyengine_us.model_api import *


class federal_parent_plus_loan_balance(Variable):
    value_type = float
    entity = Person
    label = "Federal Parent PLUS loan balance"
    documentation = (
        "Outstanding principal and interest on Federal Direct PLUS Loans the "
        "person borrowed as a parent on behalf of a dependent student, and on "
        "Direct Consolidation Loans that repaid such loans. These excepted "
        "loans cannot be repaid under the Repayment Assistance Plan; "
        "parent_plus_standard_repayment_payment repays them under the "
        "standard plan. This is the opening balance for the year. Later years "
        "hold it at its dataset (input) value, with no price or income "
        "uprating and no repayment roll-forward."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(7)",
    )
