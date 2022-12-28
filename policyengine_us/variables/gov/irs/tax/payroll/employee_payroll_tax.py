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
