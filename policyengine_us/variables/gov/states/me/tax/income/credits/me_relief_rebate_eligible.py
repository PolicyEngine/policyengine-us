from policyengine_us.model_api import *


class me_relief_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine Relief Rebate eligible"
    documentation = (
        "Eligibility for Maine's one-time $850 relief payment, determined from the "
        "2021 return and paid in 2022. PolicyEngine attributes the payment to "
        "eligibility tax year 2021. This eligibility indicator alone does not imply a "
        "payment in another year; me_relief_rebate is zero outside 2021."
    )
    defined_for = StateCode.ME
    definition_period = YEAR
    reference = "https://www.maine.gov/governor/mills/relief-checks"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.relief_rebate
        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        income_threshold = p.income_limit[filing_status]
        return federal_agi < income_threshold
