from policyengine_us.model_api import *


class employee_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "employee-side health insurance payroll tax"
    documentation = (
        "Total liability for employee-side health insurance payroll tax."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.medicare.rate
        return p.employee * person("payroll_tax_gross_wages", period)
