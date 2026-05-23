from policyengine_us.model_api import *


class nj_employee_family_leave_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee family leave insurance contribution"
    documentation = "Employee-side New Jersey family leave insurance contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        rate = parameters(
            period
        ).gov.states.nj.tax.payroll.family_leave_insurance.employee_rate
        return rate * person("nj_family_leave_insurance_taxable_wages", period)
