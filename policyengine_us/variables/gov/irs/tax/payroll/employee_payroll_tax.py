from policyengine_us.model_api import *


class employee_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "employee-side payroll tax"
    definition_period = YEAR
    unit = USD
    adds = [
        "employee_social_security_tax",
        "employee_medicare_tax",
        "additional_medicare_tax",
    ]

    def formula(person, period, parameters):
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_payroll_tax:
            return 0
        else:
            added_components = add(person, period, employee_payroll_tax.adds)
            return added_components
