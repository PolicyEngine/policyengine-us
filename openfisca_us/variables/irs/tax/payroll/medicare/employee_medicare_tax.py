from openfisca_us.model_api import *


class employee_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Employee-side health insurance payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.medicare.employee.main.rate
        return rate * person("payroll_tax_gross_wages", period)
