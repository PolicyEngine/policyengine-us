from policyengine_us.model_api import *


class mn_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Paid Leave taxable wages"
    documentation = (
        "Minnesota Paid Leave covered wages capped at the Social Security "
        "contribution and benefit base, rounded to the nearest $1,000."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.01"

    def formula(person, period, parameters):
        social_security_cap = parameters(period).gov.irs.payroll.social_security.cap
        taxable_wage_base = 1_000 * np.floor(social_security_cap / 1_000 + 0.5)
        return min_(max_(0, person("employment_income", period)), taxable_wage_base)


class employer_total_mn_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Minnesota Paid Leave taxable wages"
    documentation = (
        "Aggregate employer wages subject to Minnesota Paid Leave premiums "
        "for employer-only payroll tax calculations. Defaults to "
        "employer_total_taxable_earnings_for_social_security, which caps each "
        "worker's wages at the Social Security wage base. Minnesota caps them "
        "at that base rounded to the nearest $1,000 (Minn. Stat. 268B.01, "
        "subd. 43): $185,000 against $184,500 in 2026. The two bases differ "
        "by at most $500, so the default is off by at most $500 per worker "
        "paid above the lower one; set this input to use Minnesota's base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.01"

    def formula(person, period, parameters):
        return person("employer_total_taxable_earnings_for_social_security", period)
