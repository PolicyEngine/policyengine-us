from policyengine_us.model_api import *

EMPLOYEE_PAYROLL_TAX_COMPONENTS = [
    "employee_social_security_tax",
    "employee_medicare_tax",
    "additional_medicare_tax",
    "employee_state_payroll_tax",
]


class employee_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "employee-side payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        if parameters(period).gov.contrib.ubi_center.flat_tax.abolish_payroll_tax:
            return 0
        else:
            return add(tax_unit, period, EMPLOYEE_PAYROLL_TAX_COMPONENTS)
