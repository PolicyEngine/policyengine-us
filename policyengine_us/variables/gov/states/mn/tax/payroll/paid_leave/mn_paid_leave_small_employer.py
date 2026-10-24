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
        "(subd. 5c). The limit is a quarterly amount, which DEED states to "
        "the cent: 150 percent of $73,989 / 4 is $27,745.875 for 2026, which "
        "DEED gives as $27,745.88. DEED's "
        "further condition that the employer filed every wage detail report "
        "in the basis period is not modeled."
    )
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/268B.14",
        "https://mn.gov/deed/assets/paid-leave-small-employer-premium-rate-designation-acc_tcm1045-716947.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.tax.payroll.paid_leave.small_employer
        headcount = person("employer_headcount", period)
        average_wage = person("mn_paid_leave_employer_average_quarterly_wage", period)
        quarterly_state_average = p.state_average_annual_wage / 4
        # DEED states the limit to the cent: $27,745.875 for 2026 becomes
        # $27,745.88. Round half up, as for the taxable wage base.
        max_average_wage = (
            np.floor(100 * p.max_average_wage_ratio * quarterly_state_average + 0.5)
            / 100
        )
        # Inputs are held in float32: compare at that precision, so an input
        # of exactly the published limit meets it.
        return (headcount <= p.max_headcount) & (
            average_wage <= np.float32(max_average_wage)
        )
