from policyengine_us.model_api import *


class ma_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer paid leave contribution"
    documentation = (
        "Employer-side Massachusetts Paid Family and Medical Leave contribution, "
        "using employer headcount as a proxy for covered individuals."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        rate = p.medical_rate * (1 - p.medical_employee_share)
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return where(liable, rate * taxable_wages, 0)
