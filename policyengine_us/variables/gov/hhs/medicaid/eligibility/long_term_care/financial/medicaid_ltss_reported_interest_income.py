from policyengine_us.model_api import *


class medicaid_ltss_reported_interest_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS reported monthly interest income"
    unit = USD
    definition_period = MONTH
    default_value = -1
    documentation = (
        "Each person's actual interest receipts in the assessment month, "
        "included in their reported gross unearned income. A nonnegative "
        "amount replaces that person's annual-source default independently "
        "of other people's reports. The -1 sentinel uses annual interest "
        "income divided by twelve. Washington excludes this income for "
        "an applicant with institutional status; community-spouse interest "
        "remains income of the community spouse."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"
