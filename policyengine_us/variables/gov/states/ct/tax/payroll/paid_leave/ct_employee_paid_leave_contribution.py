from policyengine_us.model_api import *


class ct_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Connecticut employee paid leave contribution"
    documentation = "Employee-side Connecticut Paid Leave contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CT
    reference = "https://www.cga.ct.gov/current/pub/chap_557.htm#sec_31-49g"

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ct.tax.payroll.paid_leave.employee_rate
        taxable_wages = min_(
            person("payroll_tax_gross_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )
        return rate * taxable_wages
