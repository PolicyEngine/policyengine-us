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
        p = parameters(period).gov.states.nj.tax.payroll
        taxable_wages = min_(
            person("payroll_tax_gross_wages", period),
            p.temporary_disability_insurance.taxable_wage_base,
        )
        return p.family_leave_insurance.employee_rate * taxable_wages
