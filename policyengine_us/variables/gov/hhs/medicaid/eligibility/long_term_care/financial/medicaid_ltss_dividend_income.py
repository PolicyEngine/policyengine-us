from policyengine_us.model_api import *


class medicaid_ltss_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly dividend income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "When gross monthly unearned income is reported, an unspecified "
        "monthly investment source is zero; annual receipts are not mixed "
        "with an actual-month gross budget. "
        "Each person's dividend income included in gross unearned income. "
        "Defaults to annual dividend_income, the same legacy-compatible "
        "source included in gross SSI unearned income, divided by twelve, "
        "unless that person reports actual monthly dividend receipts."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340"

    def formula(person, period, parameters):
        reported = person("medicaid_ltss_reported_dividend_income", period)
        reported_gross = person("medicaid_ltss_reported_gross_unearned_income", period)
        use_annual = (reported == -1) & (reported_gross == -1)
        if not use_annual.any():
            return max_(reported, 0)
        annual_default = max_(
            person("dividend_income", period.this_year) / MONTHS_IN_YEAR, 0
        )
        return where(use_annual, annual_default, max_(reported, 0))
