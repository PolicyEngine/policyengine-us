from policyengine_us.model_api import *


class me_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maine employer paid leave contribution"
    documentation = (
        "Employer-side Maine Paid Family and Medical Leave premium: the "
        "employer half for employers with 15 or more employees (employer "
        "headcount is the proxy), plus the part of the permitted employee "
        "half the employer does not deduct, which every employer must still "
        "remit (26 M.R.S. s. 850-F(5))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME
    reference = "https://legislature.maine.gov/legis/statutes/26/title26sec850-F.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("me_paid_leave_taxable_wages", period)
        employer_share = where(liable, p.employer_rate * taxable_wages, 0)
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return employer_share + undeducted * p.employee_rate * taxable_wages
