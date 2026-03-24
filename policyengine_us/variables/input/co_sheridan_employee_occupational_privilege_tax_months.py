from policyengine_us.model_api import *


class co_sheridan_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Sheridan employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Sheridan's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0
