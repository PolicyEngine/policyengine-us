from policyengine_us.model_api import *


class ma_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employee paid leave contribution"
    documentation = (
        "Employee-side Massachusetts Paid Family and Medical Leave contribution, "
        "assuming the employer withholds the maximum permitted employee share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        rate = p.family_rate + p.medical_rate * p.medical_employee_share
        return rate * person("taxable_earnings_for_social_security", period)
