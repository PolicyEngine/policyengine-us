from policyengine_us.model_api import *


class mn_paid_leave_premium_rate(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Paid Leave premium rate"
    documentation = (
        "Minnesota Paid Leave premium rate on the person's taxable wages: the "
        "annual premium rate, or 75 percent of it for a small employer "
        "eligible under subd. 5a (Minn. Stat. 268B.14, subds. 5a(b), 6 and "
        "7). Assumes the employer participates in both the family and "
        "medical benefit programs; approved private plans (subds. 1 and 6, "
        "section 268B.10) are not modeled."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.tax.payroll.paid_leave
        small = person("mn_paid_leave_small_employer", period)
        return p.rate * where(small, p.small_employer.rate_share, 1)
