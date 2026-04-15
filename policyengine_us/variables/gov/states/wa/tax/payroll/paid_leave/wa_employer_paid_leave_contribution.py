from policyengine_us.model_api import *


class wa_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Washington employer paid leave contribution"
    documentation = (
        "Employer-side Washington Paid Family and Medical Leave contribution."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return where(liable, p.total_rate * p.employer_share * taxable_wages, 0)
