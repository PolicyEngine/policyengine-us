from policyengine_us.model_api import *


class medicaid_ltss_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly dividend income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's dividend income included in gross unearned income. "
        "Defaults to annual ordinary_dividend_income divided by twelve, "
        "unless that person reports actual monthly dividend receipts."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"

    def formula(person, period, parameters):
        reported = person("medicaid_ltss_reported_dividend_income", period)
        annual_default = max_(
            person("ordinary_dividend_income", period.this_year) / 12, 0
        )
        return where(reported == -1, annual_default, max_(reported, 0))
