from policyengine_us.model_api import *


class co_employee_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Colorado employee FAMLI contribution"
    documentation = "Employee-side Colorado FAMLI payroll contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.co.tax.payroll.famli.employee_rate
        return rate * person("taxable_earnings_for_social_security", period)
