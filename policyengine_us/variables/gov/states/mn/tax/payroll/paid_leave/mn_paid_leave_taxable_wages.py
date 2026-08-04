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
