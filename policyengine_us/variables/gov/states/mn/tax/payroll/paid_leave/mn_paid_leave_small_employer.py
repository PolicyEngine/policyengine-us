from policyengine_us.model_api import *


class mn_paid_leave_small_employer(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Paid Leave small employer"
    documentation = (
        "Whether the person's employer qualifies for the Minnesota Paid Leave "
        "small employer premium rate: 30 or fewer employees, and an average "
        "wage at most 150 percent of the state's average wage in covered "
        "employment for the basis period (Minn. Stat. 268B.14, subd. 5a(a)). "
        "employer_headcount stands in for the employer's highest quarterly "
        "employee count in the basis period (subd. 5b), and "
        "mn_paid_leave_employer_average_quarterly_wage for its average wage "
        "(subd. 5c)."
    )
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.tax.payroll.paid_leave.small_employer
        headcount = person("employer_headcount", period)
        average_wage = person("mn_paid_leave_employer_average_quarterly_wage", period)
        return (headcount <= p.max_headcount) & (
            average_wage <= p.max_average_quarterly_wage
        )
