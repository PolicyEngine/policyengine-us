from policyengine_us.model_api import *


class mn_paid_leave_permitted_employee_rate(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Paid Leave permitted employee premium rate"
    documentation = (
        "Largest share of the person's taxable wages the employer may deduct "
        "for Minnesota Paid Leave: the premium rate less the employer's "
        "minimum. The employer pays at least half the premium (Minn. Stat. "
        "268B.14, subd. 3), or for a small employer eligible under subd. 5a, "
        "at least 25 percent of the full rate out of a premium of 75 percent "
        "of it (subd. 5a(b)); employees pay the remaining portion, if any."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.tax.payroll.paid_leave
        small = person("mn_paid_leave_small_employer", period)
        premium_share_of_full_rate = where(small, p.small_employer.rate_share, 1)
        employer_minimum_share_of_full_rate = where(
            small,
            p.small_employer.employer_minimum_share,
            p.employer_minimum_share,
        )
        # Employees pay the remaining portion, if any, which is never more
        # than the premium itself.
        employee_share_of_full_rate = clip(
            premium_share_of_full_rate - employer_minimum_share_of_full_rate,
            0,
            premium_share_of_full_rate,
        )
        return p.rate * employee_share_of_full_rate
