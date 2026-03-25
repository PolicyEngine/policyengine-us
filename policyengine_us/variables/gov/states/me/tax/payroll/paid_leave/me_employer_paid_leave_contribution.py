from policyengine_us.model_api import *


class me_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maine employer paid leave contribution"
    documentation = (
        "Employer-side Maine paid leave contribution, using employer headcount "
        "as a proxy for covered employee count."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return where(liable, p.employer_rate * taxable_wages, 0)
