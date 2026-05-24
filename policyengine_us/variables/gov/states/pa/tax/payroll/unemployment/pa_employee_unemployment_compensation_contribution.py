from policyengine_us.model_api import *


class pa_employee_unemployment_compensation_contribution(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania employee unemployment compensation contribution"
    documentation = "Employee-side Pennsylvania unemployment compensation withholding."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.pa.tax.payroll.unemployment.employee_rate
        return rate * person("state_payroll_tax_gross_wages", period)
