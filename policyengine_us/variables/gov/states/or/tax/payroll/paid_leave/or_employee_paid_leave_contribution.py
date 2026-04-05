from policyengine_us.model_api import *


class or_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Oregon employee paid leave contribution"
    documentation = "Employee-side Oregon Paid Leave contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        rate = parameters(period).gov.states["or"].tax.payroll.paid_leave.employee_rate
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return rate * taxable_wages
