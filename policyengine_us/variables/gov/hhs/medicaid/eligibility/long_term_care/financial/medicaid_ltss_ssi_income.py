from policyengine_us.model_api import *


class medicaid_ltss_ssi_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly SSI receipts"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Supplemental Security Income receipts included in a person's "
        "reported gross monthly unearned income. Washington excludes "
        "these receipts under WAC 182-513-1340(1)(f). Defaults to zero "
        "because the annual-source gross unearned-income default already "
        "omits SSI. Report only amounts also included in gross unearned "
        "income, without duplicating state public-assistance receipts."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"
