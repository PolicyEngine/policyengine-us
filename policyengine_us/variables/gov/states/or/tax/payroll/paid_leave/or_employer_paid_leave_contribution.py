from policyengine_us.model_api import *


class or_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Oregon employer paid leave contribution"
    documentation = "Employer-side Oregon Paid Leave contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return where(liable, p.employer_rate * taxable_wages, 0)
