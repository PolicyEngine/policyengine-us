from policyengine_us.model_api import *


class ct_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Connecticut employee paid leave contribution"
    documentation = "Employee-side Connecticut Paid Leave contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CT

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ct.tax.payroll.paid_leave.employee_rate
        return rate * person("taxable_earnings_for_social_security", period)
