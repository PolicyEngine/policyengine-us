from policyengine_us.model_api import *


class dc_employer_paid_leave_tax(Variable):
    value_type = float
    entity = Person
    label = "District of Columbia employer paid leave tax"
    documentation = "Employer-side District of Columbia Paid Family Leave tax."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.dc.tax.payroll.paid_leave.employer_rate
        return rate * person("payroll_tax_gross_wages", period)
