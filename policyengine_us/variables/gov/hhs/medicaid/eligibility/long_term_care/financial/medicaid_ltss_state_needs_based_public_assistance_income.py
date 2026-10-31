from policyengine_us.model_api import *


class medicaid_ltss_state_needs_based_public_assistance_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly state needs-based public-assistance receipts"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "State public-assistance receipts based on financial need that "
        "qualify under WAC 182-513-1340(1)(f), included in the person's "
        "reported gross monthly unearned income. These are factual "
        "payments, distinct from the broader needs-based income input "
        "used for Delaware's general exclusion. Defaults to zero because "
        "the annual-source gross default omits these payments. Report "
        "only amounts included in gross unearned income, without "
        "duplicating SSI receipts."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"
