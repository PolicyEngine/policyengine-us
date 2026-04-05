from policyengine_us.model_api import *


class me_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maine employee paid leave contribution"
    documentation = (
        "Employee-side Maine paid leave contribution, assuming the employer "
        "withholds the maximum permitted employee share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.me.tax.payroll.paid_leave.employee_rate
        return rate * person("taxable_earnings_for_social_security", period)
