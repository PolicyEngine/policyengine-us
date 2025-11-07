from policyengine_us.model_api import *


class payroll_tax_revenue_social_security(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security payroll tax revenue"
    documentation = (
        "OASDI payroll tax revenue from employee and employer contributions"
    )
    unit = USD
    adds = ["employee_social_security_tax", "employer_social_security_tax"]
