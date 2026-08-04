from policyengine_us.model_api import *


class mn_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Minnesota employee paid leave contribution"
    documentation = (
        "Employee-side Minnesota Paid Leave contribution, assuming the employer "
        "withholds the maximum permitted employee share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.mn.tax.payroll.paid_leave.employee_rate
        return rate * person("mn_paid_leave_taxable_wages", period)
