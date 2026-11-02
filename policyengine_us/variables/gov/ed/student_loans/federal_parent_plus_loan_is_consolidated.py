from policyengine_us.model_api import *


class federal_parent_plus_loan_is_consolidated(Variable):
    value_type = bool
    entity = Person
    label = "Parent PLUS loan balance is a Direct Consolidation Loan"
    documentation = (
        "The person's federal_parent_plus_loan_balance is a Direct "
        "Consolidation Loan that repaid parent PLUS loans and entered "
        "repayment from July 1, 2006 through June 30, 2026. Its standard "
        "repayment plan runs 10 to 30 years depending on the total of the "
        "consolidation loan and the borrower's other education loans, "
        "instead of 10 years. Leave it false for unconsolidated parent PLUS "
        "loans and for consolidation loans that entered repayment before July "
        "1, 2006, which repay over 10 years."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.220#p-685.220(i)(2)(ii)",
    )
