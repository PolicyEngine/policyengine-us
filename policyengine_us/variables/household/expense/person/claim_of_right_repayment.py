from policyengine_us.model_api import *


class claim_of_right_repayment(Variable):
    value_type = float
    entity = Person
    label = "Repayment of income received under a claim of right"
    unit = USD
    documentation = (
        "Amount repaid this year of income that was included in adjusted gross "
        "income in an earlier year because it appeared the person had an "
        "unrestricted right to it (26 U.S.C. 1341). Excludes repayments deducted "
        "in arriving at adjusted gross income this year."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1341"
