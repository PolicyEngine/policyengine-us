from policyengine_us.model_api import *


class ny_employee_paid_family_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "New York employee paid family leave contribution"
    documentation = "Employee-side New York Paid Family Leave contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.payroll.paid_family_leave
        uncapped = p.employee_rate * person("payroll_tax_gross_wages", period)
        return min_(uncapped, p.annual_max_contribution)
