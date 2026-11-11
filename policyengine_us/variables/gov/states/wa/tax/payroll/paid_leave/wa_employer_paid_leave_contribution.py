from policyengine_us.model_api import *


class wa_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Washington employer paid leave contribution"
    documentation = (
        "Employer-side Washington Paid Family and Medical Leave premium: the "
        "employer portion for employers with 50 or more employees (employer "
        "headcount is the proxy), plus the part of the permitted employee "
        "share the employer does not deduct, which it is treated as electing "
        "to pay (WAC 192-510-065(2))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=50A.10.030",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=192-510-065",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("wa_paid_leave_taxable_wages", period)
        employer_share = where(
            liable, p.total_rate * p.employer_share * taxable_wages, 0
        )
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return (
            employer_share
            + undeducted * p.total_rate * (1 - p.employer_share) * taxable_wages
        )
