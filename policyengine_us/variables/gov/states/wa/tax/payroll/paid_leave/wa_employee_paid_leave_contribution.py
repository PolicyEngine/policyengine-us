from policyengine_us.model_api import *


class wa_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Washington employee paid leave contribution"
    documentation = (
        "Employee-side Washington Paid Family and Medical Leave contribution."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return p.total_rate * (1 - p.employer_share) * taxable_wages
