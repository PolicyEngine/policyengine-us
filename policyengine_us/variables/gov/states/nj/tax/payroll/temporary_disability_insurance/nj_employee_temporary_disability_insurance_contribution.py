from policyengine_us.model_api import *


class nj_employee_temporary_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee temporary disability insurance contribution"
    documentation = (
        "Employee-side New Jersey temporary disability insurance contribution."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.temporary_disability_insurance
        taxable_wages = min_(
            person("payroll_tax_gross_wages", period), p.taxable_wage_base
        )
        return p.employee_rate * taxable_wages
