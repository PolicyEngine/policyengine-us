from policyengine_us.model_api import *


class co_glendale_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Glendale employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Glendale's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0
