from policyengine_us.model_api import *


class medicaid_ltss_interest_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly interest income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's interest income included in gross unearned income. "
        "Defaults to annual interest_income divided by twelve, unless "
        "that person reports actual monthly interest receipts."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"

    def formula(person, period, parameters):
        reported = person("medicaid_ltss_reported_interest_income", period)
        annual_default = max_(person("interest_income", period.this_year) / 12, 0)
        return where(reported == -1, annual_default, max_(reported, 0))
